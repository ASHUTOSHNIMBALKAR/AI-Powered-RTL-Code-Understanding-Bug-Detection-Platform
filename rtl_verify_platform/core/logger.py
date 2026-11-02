import logging
import sys
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Shared premium console instance
console = Console(force_terminal=True)

def setup_logger(name: str = "rtl_verify", level: int = logging.INFO) -> logging.Logger:
    """Sets up a highly styled rich logger for console outputs."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)
    logger.addHandler(rich_handler)
    
    return logger

# Default platform-wide logger
logger = setup_logger()
