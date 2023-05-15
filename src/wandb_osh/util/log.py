# std
from __future__ import annotations

import logging

import colorlog

LOG_DEFAULT_LEVEL = logging.DEBUG


def get_logger():
    """Sets up global logger."""
    _log = colorlog.getLogger("wandb_osh")

    if _log.handlers:
        # the logger already has handlers attached to it, even though
        # we didn't add it ==> logging.get_logger got us an existing
        # logger ==> we don't need to do anything
        return _log

    _log.setLevel(LOG_DEFAULT_LEVEL)

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

    _log.addHandler(sh)

    return _log


logger = get_logger()
