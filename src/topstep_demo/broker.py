from typing import Protocol, List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger("topstep_demo.broker")

@dataclass
class Trade:
    timestamp: datetime
    symbol: str
    side: str  # BUY or SELL
    qty: int
    price: float
    order_id: str
    realized_pnl: Optional[float] = None

class Broker(Protocol):
    def get_cash(self) -> float: ...
    def get_position(self, symbol: str) -> int: ...
    def get_average_entry(self, symbol: str) -> float: ...
    def place_order(self, symbol: str, qty: int, side: str, price: float, timestamp: datetime) -> str: ...
    def get_trades(self) -> List[Trade]: ...
    def get_realized_pnl(self) -> float: ...

class MockBroker:
    def __init__(self, initial_cash: float = 100_000.0, allow_short: bool = False):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.allow_short = allow_short
        
        self.positions: Dict[str, int] = {}
        self.avg_entries: Dict[str, float] = {} # Track avg entry price
        
        self.trades: List[Trade] = []
        self._order_counter = 0
        self._realized_pnl = 0.0

    def get_cash(self) -> float:
        return self.cash
        
    def get_realized_pnl(self) -> float:
        return self._realized_pnl

    def get_position(self, symbol: str) -> int:
        return self.positions.get(symbol, 0)
        
    def get_average_entry(self, symbol: str) -> float:
        return self.avg_entries.get(symbol, 0.0)

    def place_order(self, symbol: str, qty: int, side: str, price: float, timestamp: datetime) -> str:
        """
        Execute an assumed market order fill at the given price.
        Enforces Long-Only if allow_short is False.
        """
        side = side.upper()
        current_pos = self.positions.get(symbol, 0)
        
        # Rule Check: Long-Only
        if not self.allow_short:
            # Cannot SELL if we don't have a position
            if side == "SELL" and current_pos <= 0:
                logger.warning(f"REJECTED: Sell {qty} {symbol} - Short selling disabled and no long position.")
                return ""
                
            # Cannot Sell more than we own (no net short)
            if side == "SELL" and (current_pos - qty) < 0:
                 logger.warning(f"REJECTED: Sell {qty} {symbol} - Cannot flip to net short.")
                 return ""

        self._order_counter += 1
        order_id = f"ORD-{self._order_counter:04d}"
        
        cost = qty * price
        trade_pnl = None
        
        if side == "BUY":
            # Opening (or adding to) Long, OR Closing Short
            
            # If we are Short, this BUY is closing/reducing
            if current_pos < 0:
                # Calculate PnL on the portion closed
                # Entry: avg_entry, Exit: price. Short profit = Entry - Exit
                avg_entry = self.avg_entries.get(symbol, 0.0)
                qty_closing = min(abs(current_pos), qty)
                pnl = (avg_entry - price) * qty_closing
                self._realized_pnl += pnl
                trade_pnl = pnl
                
            # Update Avg Entry?
            # If flipping from Short to Long, or adding to Long.
            # Simplified: Weighted Average if Adding to Same Side. 
            # Reset if flipping.
            new_pos = current_pos + qty
            if current_pos >= 0:
                # Adding to Long
                total_val = (current_pos * self.avg_entries.get(symbol, 0.0)) + (qty * price)
                self.avg_entries[symbol] = total_val / new_pos if new_pos != 0 else 0.0
            elif new_pos > 0:
                # Flipped from Short to Long
                # The remaining qty is new Long
                self.avg_entries[symbol] = price
            
            self.cash -= cost
            self.positions[symbol] = new_pos
            
        elif side == "SELL":
            # Opening Short, OR Closing Long
            
            # If we are Long, this SELL is closing/reducing
            if current_pos > 0:
                # Calculate PnL
                # Entry: avg_entry, Exit: price. Long profit = Exit - Entry
                avg_entry = self.avg_entries.get(symbol, 0.0)
                qty_closing = min(current_pos, qty)
                pnl = (price - avg_entry) * qty_closing
                self._realized_pnl += pnl
                trade_pnl = pnl
                
            # Update Avg Entry?
            new_pos = current_pos - qty
            if current_pos <= 0:
                # Adding to Short
                # Note: keeping avg_entry positive for calc
                total_val = (abs(current_pos) * self.avg_entries.get(symbol, 0.0)) + (qty * price)
                self.avg_entries[symbol] = total_val / abs(new_pos) if new_pos != 0 else 0.0
            elif new_pos < 0:
                # Flipped from Long to Short
                self.avg_entries[symbol] = price
                
            self.cash += cost
            self.positions[symbol] = new_pos
        else:
            raise ValueError(f"Invalid side: {side}")
            
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            side=side,
            qty=qty,
            price=price,
            order_id=order_id,
            realized_pnl=trade_pnl
        )
        self.trades.append(trade)
        
        pnl_str = f" | PnL: ${trade_pnl:.2f}" if trade_pnl is not None else ""
        logger.info(f"FILLED: {side} {qty} {symbol} @ {price:.2f}{pnl_str} | Id: {order_id} | Pos: {self.positions[symbol]}")
        return order_id
        
    def get_trades(self) -> List[Trade]:
        return self.trades
