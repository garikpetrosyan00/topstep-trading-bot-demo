import logging
import sys
from rich.logging import RichHandler

def setup_logging(level: str = "INFO"):
    """
    Configure structured logging using RichHandler for clean, professional output.
    """
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
    )

    # Silence chatty libraries if any added later
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str):
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
