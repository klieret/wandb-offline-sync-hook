from __future__ import annotations

import os

from gnn_tracking.utils.log import logger

logger.info("Setting test mode")
os.environ["WANDB_OSH_TESTING"] = "True"
