from __future__ import annotations

import logging

from wandb_osh.util.log import get_logger, logger
from wandb_osh import set_log_level


def test_logger():
    logger.info("Hello world")


def test_get_logger():
    assert isinstance(get_logger(), logging.Logger)


def test_set_log_level():
    set_log_level("ERROR")
    assert get_logger().level == logging.ERROR
    set_log_level()
