import logging
import sys

def setup_logger(name: str = "bot") -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.handlers:
                # Already configured
                return logger

        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
        return logger