import time
import logging
from typing import Optional, List

from .config import BotConfig
from .broker import MockBroker
from .strategy import MovingAverageCrossoverStrategy
from .risk import RiskManager
from .data import load_price_feed
from .logging_utils import get_logger
from .report import generate_report

logger = get_logger("topstep_demo.runner")

def run_simulation(config: BotConfig, fast_mode: bool = False, csv_path: Optional[str] = None):
    """
    Run the main simulation loop.
    """
    mode_name = "BACKTEST" if fast_mode else "SIMULATION"
    logger.info(f"Starting {mode_name} | {config.symbol} | Qty: {config.qty} | AllowShort: {config.allow_short}")
    
    # Initialize components
    broker = MockBroker(initial_cash=config.initial_cash, allow_short=config.allow_short)
    strategy = MovingAverageCrossoverStrategy(fast_window=config.fast_ma, slow_window=config.slow_ma)
    risk_manager = RiskManager(config, broker)
    
    # Price Feed
    if csv_path:
        from pathlib import Path
        feed = load_price_feed(Path(csv_path))
    else:
        from pathlib import Path
        default_path = Path("data/sample_prices.csv")
        feed = load_price_feed(default_path)

    start_time = time.time()
    
    equity_curve: List[float] = []
    
    for timestamp, price in feed:
        
        # 1. Strategy Signal
        signal = strategy.on_price(timestamp, price)
        
        # 2. Risk Management
        # Check Exits
        exit_action = risk_manager.check_exit(price, timestamp)
        if exit_action:
            broker.place_order(config.symbol, config.qty, exit_action, price, timestamp)
            risk_manager.update_position_state(exit_action, price, timestamp)
        elif exit_action is None:
            # Check Entries (if strategy says so)
            # Strategy says BUY or SELL. 
            # If strategy says SELL, Risk Manager only allows if we are Long (to close) OR if Shorting is allowed.
            if signal != "HOLD":
                # Check with Risk Manager first
                if risk_manager.check_entry(signal, price, timestamp):
                    broker.place_order(config.symbol, config.qty, signal, price, timestamp)
                    risk_manager.update_position_state(signal, price, timestamp)
                # Note: Strategy 'SELL' might be intended as Exit.
                # If we are long, Strategy 'SELL' is a valid exit signal too (Trend Reversal).
                # Risk Manager check_exit usually handles SL/TP.
                # But Strategy Exit needs to be handled here.
                # If we have a position, and signal opposes it, we should exit.
                pos = broker.get_position(config.symbol)
                if pos > 0 and signal == "SELL":
                    broker.place_order(config.symbol, config.qty, "SELL", price, timestamp)
                    risk_manager.update_position_state("SELL", price, timestamp)
                elif pos < 0 and signal == "BUY":
                    broker.place_order(config.symbol, config.qty, "BUY", price, timestamp)
                    risk_manager.update_position_state("BUY", price, timestamp)

        # Track Equity
        pos_val = broker.get_position(config.symbol) * price
        # For short, pos is negative. Value liability.
        # Cash + Position Value is misleading for Futures/Shorts in simple terms but:
        # Equity = Cash + Unrealized PnL? 
        # Simpler: Equity = Cash + (Pos * Price) ? 
        # Correct for Long.
        # For Short: We sold 1 @ 100. Cash += 100. Pos = -1.
        # Current Price = 110. Equity = (100 + 100) + (-1 * 110) = 200 - 110 = 90. Correct.
        eq = broker.get_cash() + pos_val
        equity_curve.append(eq)
        
        # Delay
        if not fast_mode:
            time.sleep(0.05) 
            
    end_time = time.time()
    
    # Report
    generate_report(broker.get_trades(), broker.get_cash(), config.initial_cash, equity_curve)
