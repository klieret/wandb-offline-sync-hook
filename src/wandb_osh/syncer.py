from __future__ import annotations

import os
import subprocess
import time
from os import PathLike
from pathlib import Path

from wandb_osh import __version__
from wandb_osh.config import _command_dir_default
from wandb_osh.util.log import logger


class WandbSyncer:
    def __init__(
        self,
        command_dir: PathLike = _command_dir_default,
        wait: int = 1,
        wandb_options: list[str] | None = None,
    ):
        """Class for interpreting command files and triggering
        `wandb sync`.

        Args:
            command_dir: Directory used for communication
            wait: Minimal time to wait before scanning command dir again
            wandb_options: Options to pass on to wandb
        """
        if wandb_options is None:
            wandb_options = []
        self.command_dir = Path(command_dir)
        self.wait = wait
        self.wandb_options = wandb_options

    def sync(self, dir: PathLike) -> None:
        """Sync a directory. Thin wrapper around the `sync_dir` function.

        Args:
            dir: Directory with wandb files to be synced
        """
        sync_dir(dir, options=self.wandb_options)

    def loop(self) -> None:
        """Read command files and trigger syncing"""
        logger.info(
            "wandb-osh v%s, starting to watch %s", __version__, self.command_dir
        )
        while True:
            start_time = time.time()
            self.command_dir.mkdir(parents=True, exist_ok=True)
            command_files = []
            targets = []
            for command_file in self.command_dir.glob("*.command"):
                target = Path(command_file.read_text())
                command_files.append(command_file)
                if not target.is_dir():
                    logger.error(
                        "Command file %s points to non-existing directory %s",
                        command_file,
                        target,
                    )
                    continue
                targets.append(target)
            for target in set(targets):
                logger.info("Syncing %s...", target)
                self.sync(target)
            time.sleep(0.25)
            for cf in command_files:
                if cf.is_file():
                    cf.unlink()
            if "PYTEST_CURRENT_TEST" in os.environ:
                break
            time.sleep(max(0.0, (time.time() - start_time) - self.wait))


def sync_dir(dir: PathLike, options: list[str] | None = None) -> None:
    """Call wandb sync on a directory.

    Args:
        dir: Directory with wandb runs
        options: List of options to pass on to `wandb sync`
    """
    if options is None:
        options = []
    dir = Path(dir)
    command = ["wandb", "sync", *options, "."]
    if "PYTEST_CURRENT_TEST" in os.environ:
        logger.debug("Testing mode enabled. Not actually calling wandb.")
        logger.debug("Command would be: %s in %s", " ".join(command), dir)
        return
    subprocess.run(command, cwd=dir)
