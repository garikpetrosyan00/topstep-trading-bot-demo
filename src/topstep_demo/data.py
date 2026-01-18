import csv
from pathlib import Path
from typing import Iterator, Tuple, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger("topstep_demo.data")

def load_price_feed(csv_path: Optional[Path] = None) -> Iterator[Tuple[datetime, float]]:
    """
    Load price data from a CSV file or fallback to an in-memory generator.
    Yields (timestamp, price) tuples.
    """
    if csv_path and csv_path.exists():
        logger.info(f"Loading prices from {csv_path}")
        try:
            with open(csv_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Expecting 'timestamp' and 'price' columns
                    # Assuming timestamp is ISO format or close to it
                    try:
                        ts = datetime.fromisoformat(row['timestamp'])
                        price = float(row['price'])
                        yield ts, price
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid row {row}: {e}")
            return
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}. Falling back to default feed.")
    
    logger.info("Using default in-memory price feed.")
    # Fallback synthetic data: Simple sine wave + trend or random walk
    # Just a small fixed list for demo if file missing
    base_price = 4000.0
    start_time = datetime.now()
    # 20 steps of synthetic data
    import timedelta
    from datetime import timedelta
    
    prices = [
        4000.0, 4005.0, 4010.0, 4008.0, 4012.0, 
        4015.0, 4020.0, 4018.0, 4025.0, 4030.0,
        4028.0, 4022.0, 4015.0, 4010.0, 4005.0,
        4000.0, 3995.0, 3990.0, 3985.0, 3980.0
    ]
    
    for i, p in enumerate(prices):
        yield start_time + timedelta(minutes=i), p
