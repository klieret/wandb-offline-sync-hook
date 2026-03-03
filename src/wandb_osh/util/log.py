from __future__ import annotations
import logging
import os

logger = logging.getLogger("wandb_osh")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.NOTSET)

LOG_DEFAULT_LEVEL = logging.INFO

try:
    import colorlog
except ImportError:
    colorlog = None

def _enable_colorlog_if_requested() -> None:
    if os.getenv("WANDB_OSH_COLORLOG", "0") != "1":
        return
    if colorlog is None:
        return

    if any(h.__class__.__name__ == "StreamHandler" for h in logger.handlers):
        return

    sh = colorlog.StreamHandler()
    log_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    }
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s %(levelname)s: %(message)s",
        log_colors=log_colors,
        datefmt="%H:%M:%S",
    )
    sh.setFormatter(formatter)
    # Controlled by overall logger level
    sh.setLevel(logging.DEBUG)

    logger.addHandler(sh)


def get_logger():
    _enable_colorlog_if_requested()
    return logger


def set_log_level(level: str | int = LOG_DEFAULT_LEVEL) -> None:
    get_logger()
    logger.setLevel(level)
