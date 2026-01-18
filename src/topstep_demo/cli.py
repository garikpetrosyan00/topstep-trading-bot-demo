import argparse
from .runner import run_simulation
from .config import BotConfig
from .logging_utils import setup_logging

def main():
    parser = argparse.ArgumentParser(description="Topstep Trading Bot Demo")
    
    parser.add_argument("--symbol", type=str, default="SIM-ES", help="Trading Symbol")
    parser.add_argument("--qty", type=int, default=1, help="Order Quantity")
    parser.add_argument("--sl-pct", type=float, default=0.01, help="Stop Loss Percentage")
    parser.add_argument("--tp-pct", type=float, default=0.02, help="Take Profit Percentage")
    parser.add_argument("--initial-cash", type=float, default=100_000.0, help="Initial Cash")
    parser.add_argument("--allow-short", action="store_true", help="Allow Short Selling")
    
    parser.add_argument("--fast-ma", type=int, default=10, help="Fast MA Window")
    parser.add_argument("--slow-ma", type=int, default=20, help="Slow MA Window")
    
    parser.add_argument("--csv", type=str, help="Custom CSV")
    
    # Mode selection
    parser.add_argument("--mode", type=str, choices=["backtest", "sim"], default="backtest", 
                        help="Run mode: backtest (fast, no delay) or sim (real-time simulation)")
    parser.add_argument("--fast", action="store_true", help="Legacy flag, alias for --mode backtest")
    
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    # Handle legacy fast flag
    is_fast = args.mode == "backtest" or args.fast
    
    config = BotConfig(
        symbol=args.symbol,
        qty=args.qty,
        sl_pct=args.sl_pct,
        tp_pct=args.tp_pct,
        allow_short=args.allow_short,
        initial_cash=args.initial_cash,
        fast_ma=args.fast_ma,
        slow_ma=args.slow_ma
    )
    
    run_simulation(config, fast_mode=is_fast, csv_path=args.csv)

if __name__ == "__main__":
    main()
