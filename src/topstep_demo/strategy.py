from typing import Protocol, Optional
from collections import deque
import logging

logger = logging.getLogger("topstep_demo.strategy")

class Strategy(Protocol):
    def on_price(self, timestamp, price: float) -> str:
        """Return 'BUY', 'SELL', or 'HOLD'"""
        ...

class MovingAverageCrossoverStrategy:
    """
    Moving Average Crossover.
    BUY when Fast MA crosses above Slow MA.
    SELL when Fast MA crosses below Slow MA.
    """
    def __init__(self, fast_window: int = 10, slow_window: int = 20):
        self.fast_window = fast_window
        self.slow_window = slow_window
        
        self.prices = deque(maxlen=slow_window + 1) # Need enough for slow
        self.prev_fast = None
        self.prev_slow = None
        
        logger.info(f"Strategy: MA Crossover ({fast_window}/{slow_window})")

    def on_price(self, timestamp, price: float) -> str:
        self.prices.append(price)
        
        # Warmup
        if len(self.prices) < self.slow_window:
            return "HOLD"
            
        # Calculate MAs
        # Note: In real app, optimize this (incremental update or pandas)
        # For demo with deque, slicing is fine.
        curr_fast = sum(list(self.prices)[-self.fast_window:]) / self.fast_window
        curr_slow = sum(list(self.prices)[-self.slow_window:]) / self.slow_window
        
        signal = "HOLD"
        
        if self.prev_fast is not None and self.prev_slow is not None:
            # Crossover Logic
            # Bullish Cross
            if self.prev_fast <= self.prev_slow and curr_fast > curr_slow:
                signal = "BUY"
            # Bearish Cross
            elif self.prev_fast >= self.prev_slow and curr_fast < curr_slow:
                signal = "SELL"
                
        self.prev_fast = curr_fast
        self.prev_slow = curr_slow
        
        return signal
