from __future__ import annotations

import os
import subprocess
import time
from os import PathLike
from pathlib import Path

from gnn_tracking.utils.log import logger

from wandb_osh.config import _command_dir_default


class WandbSyncer:
    def __init__(self, command_dir: PathLike = _command_dir_default, wait: int = 1):
        self.command_dir = Path(command_dir)
        self.wait = wait

    def sync(self, dir: PathLike):
        """Sync a directory.

        Args:
            dir: Directory with wandb files to be synced
        """
        sync_dir(dir)

    def _handle_command_file(self, command_file: Path):
        dir = Path(command_file.read_text())
        if not dir.is_dir():
            logger.error(
                "Command file %s points to non-existing directory %s",
                command_file,
                dir,
            )
            command_file.unlink()
            return
        logger.info("Syncing %s...", dir)
        self.sync(dir)
        logger.info("Syncing Done")
        command_file.unlink()

    def loop(self):
        logger.info("Starting to watch %s", self.command_dir)
        while True:
            start_time = time.time()
            self.command_dir.mkdir(parents=True, exist_ok=True)
            for command_file in self.command_dir.glob("*.command"):
                self._handle_command_file(command_file)
            if "PYTEST_CURRENT_TEST" in os.environ:
                break
            time.sleep(max(0.0, (time.time() - start_time) - self.wait))


def sync_dir(dir: PathLike) -> None:
    """Call wandb sync on a directory."""
    dir = Path(dir)
    command = ["wandb", "sync", "--sync-all"]
    if "PYTEST_CURRENT_TEST" in os.environ:
        logger.debug("Testing mode enabled. Not actually calling wandb.")
        logger.debug("Command would be: %s in %s", " ".join(command), dir)
        return
    subprocess.run(command, cwd=dir)
