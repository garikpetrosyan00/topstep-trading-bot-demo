from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration for the trading bot."""
    symbol: str
    qty: int
    sl_pct: float
    tp_pct: float
    max_positions: int = 1
    
    # New params
    allow_short: bool = False
    initial_cash: float = 100_000.0
    fast_ma: int = 10
    slow_ma: int = 20
