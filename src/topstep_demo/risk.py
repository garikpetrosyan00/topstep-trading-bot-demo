from dataclasses import dataclass
from typing import Optional
import logging
from .config import BotConfig
from .broker import Broker

logger = logging.getLogger("topstep_demo.risk")

@dataclass
class PositionMetadata:
    entry_price: float
    timestamp: object 
    side: str # 'LONG' or 'SHORT'
    sl_price: float
    tp_price: float

class RiskManager:
    def __init__(self, config: BotConfig, broker: Broker):
        self.config = config
        self.broker = broker
        self.active_position: Optional[PositionMetadata] = None

    def check_entry(self, signal: str, current_price: float, timestamp) -> bool:
        """
        Check if we can enter a new trade.
        """
        current_pos_size = self.broker.get_position(self.config.symbol)
        
        # Rule: One position at a time
        if current_pos_size != 0:
            return False
            
        if signal == "BUY":
            return True
            
        if signal == "SELL":
            # Only allow short entry if configured
            return self.config.allow_short
            
        return False
        
    def check_exit(self, current_price: float, timestamp) -> Optional[str]:
        """
        Check for SL/TP hits.
        Returns 'BUY' or 'SELL' action to CLOSE the position, or None.
        """
        pos_qty = self.broker.get_position(self.config.symbol)
        if pos_qty == 0:
            self.active_position = None
            return None
            
        # Recover state if missing (e.g. restart) - minimal fallback
        if not self.active_position:
            avg_entry = self.broker.get_average_entry(self.config.symbol)
            direction = "LONG" if pos_qty > 0 else "SHORT"
            # Recalculate default SL/TP based on current average entry
            if direction == "LONG":
                sl = avg_entry * (1 - self.config.sl_pct)
                tp = avg_entry * (1 + self.config.tp_pct)
            else:
                sl = avg_entry * (1 + self.config.sl_pct)
                tp = avg_entry * (1 - self.config.tp_pct)
                
            self.active_position = PositionMetadata(avg_entry, timestamp, direction, sl, tp)
            
        ap = self.active_position
        
        if ap.side == "LONG":
            # Stop Loss (Price drops)
            if current_price <= ap.sl_price:
                logger.debug(f"STOP LOSS HIT: Long Entry {ap.entry_price} | SL {ap.sl_price} | Curr {current_price}")
                return "SELL"
            # Take Profit (Price rises)
            if current_price >= ap.tp_price:
                logger.debug(f"TAKE PROFIT HIT: Long Entry {ap.entry_price} | TP {ap.tp_price} | Curr {current_price}")
                return "SELL"
                
        elif ap.side == "SHORT":
            # Stop Loss (Price rises)
            if current_price >= ap.sl_price:
                logger.debug(f"STOP LOSS HIT: Short Entry {ap.entry_price} | SL {ap.sl_price} | Curr {current_price}")
                return "BUY"
            # Take Profit (Price drops)
            if current_price <= ap.tp_price:
                logger.debug(f"TAKE PROFIT HIT: Short Entry {ap.entry_price} | TP {ap.tp_price} | Curr {current_price}")
                return "BUY"
                
        return None

    def update_position_state(self, side: str, price: float, timestamp):
        """
        Called trigger post-fill.
        If we just opened a position, record metadata (SL/TP).
        If we closed, clear it.
        """
        pos = self.broker.get_position(self.config.symbol)
        
        if pos == 0:
            self.active_position = None
        elif not self.active_position:
            # We just opened a position
            direction = "LONG" if pos > 0 else "SHORT"
            
            if direction == "LONG":
                sl = price * (1 - self.config.sl_pct)
                tp = price * (1 + self.config.tp_pct)
            else:
                sl = price * (1 + self.config.sl_pct)
                tp = price * (1 - self.config.tp_pct)
                
            self.active_position = PositionMetadata(
                entry_price=price, 
                timestamp=timestamp, 
                side=direction,
                sl_price=sl,
                tp_price=tp
            )
            logger.debug(f"Risk Params Set: {direction} @ {price} | SL: {sl:.2f} | TP: {tp:.2f}")
