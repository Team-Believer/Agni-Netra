import logging
import sys

def setup_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("agni_netra")
    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(module)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger

logger = setup_logging()
