from __future__ import annotations

import os
import subprocess
import time
from multiprocessing import Process, Queue
from os import PathLike
from pathlib import Path
from queue import Empty

from wandb_osh import __version__
from wandb_osh.config import _command_dir_default
from wandb_osh.util.log import logger


class WandbSyncer:
    def __init__(
        self,
        command_dir: PathLike = _command_dir_default,
        wait: int = 1,
        wandb_options: list[str] | None = None,
        *,
        timeout: int | float = 120,
        num_workers: int = 1,
    ):
        """Class for interpreting command files and triggering
        `wandb sync`.

        Args:
            command_dir: Directory used for communication
            wait: Minimal time to wait before scanning command dir again
            wandb_options: Options to pass on to wandb
            timeout: Timeout for wandb sync. If <=0, no timeout.
        """
        if wandb_options is None:
            wandb_options = []
        self.command_dir = Path(command_dir)
        self.wait = wait
        self.wandb_options = wandb_options
        self._timeout = timeout
        self.num_workers = num_workers
        self.target_queue: Queue = Queue()
        self.workers: list[Process] = []

    def start(self) -> None:
        """Start directory watcher process and sync workers

        Args:
            None
        """
        watcher = Process(target=self.dir_watcher)
        watcher.start()

        self.command_dir.mkdir(parents=True, exist_ok=True)

        for _ in range(self.num_workers):
            p = Process(target=self.worker)
            self.workers.append(p)
            p.start()

    def sync(self, dir: PathLike) -> None:
        """Sync a directory. Thin wrapper around the `sync_dir` function.

        Args:
            dir: Directory with wandb files to be synced
        """
        sync_dir(dir, options=self.wandb_options, timeout=self._timeout)

    def dir_watcher(self) -> None:
        """Read command files and trigger syncing"""
        logger.info(
            "wandb-osh v%s, starting to watch %s", __version__, self.command_dir
        )
        while True:
            start_time = time.time()
            self.command_dir.mkdir(parents=True, exist_ok=True)
            for command_file in self.command_dir.glob("*.command"):
                target = Path(command_file.read_text())
                if not target.is_dir():
                    logger.error(
                        "Command file %s points to non-existing directory %s",
                        command_file,
                        target,
                    )
                    continue
                self.target_queue.put((command_file, target))
            time.sleep(max(0.0, (time.time() - start_time) - self.wait))

    def worker(self) -> None:
        while True:
            try:
                cf, target = self.target_queue.get(timeout=self._timeout)
                self.sync(target)
                time.sleep(0.25)
                if cf.is_file():
                    cf.unlink()
                if "PYTEST_CURRENT_TEST" in os.environ:
                    break
            except Empty:
                # try again later
                logger.warning("Syncing %s timed out. Trying later.", target)
                from wandb_osh.hooks import TriggerWandbSyncHook

                TriggerWandbSyncHook(self.command_dir)(target)


def sync_dir(
    dir: PathLike, options: list[str] | None = None, *, timeout: int | float = 0
) -> None:
    """Call wandb sync on a directory.

    Args:
        dir: Directory with wandb runs
        options: List of options to pass on to `wandb sync`
        timeout: Timeout for wandb sync. If <=0: no timeout
    """
    if options is None:
        options = []
    dir = Path(dir)
    command = ["wandb", "sync", *options, "."]
    if "PYTEST_CURRENT_TEST" in os.environ:
        logger.debug("Testing mode enabled. Not actually calling wandb.")
        logger.debug("Command would be: %s in %s", " ".join(command), dir)
        return
    _timeout = None if timeout <= 0 else timeout
    subprocess.run(command, cwd=dir, timeout=_timeout)
