from __future__ import annotations

import os
import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor, wait
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
        *,
        timeout: int | float = 120,
        max_workers: int = 1,
    ):
        """Class for interpreting command files and triggering
        `wandb sync`.

        Args:
            command_dir: Directory used for communication
            wait: Minimal time to wait before scanning command dir again
            wandb_options: Options to pass on to wandb
            timeout: Timeout for wandb sync. If <=0, no timeout.
            max_workers: Maximum number of concurrent sync processes.
        """
        if wandb_options is None:
            wandb_options = []
        if max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        self.command_dir = Path(command_dir)
        self.wait = wait
        self.wandb_options = wandb_options
        self._timeout = timeout
        self.max_workers = max_workers
        self._pending: set[Path] = set()
        self._in_progress: dict[Future, Path] = {}

    def sync(self, dir: PathLike) -> None:
        """Sync a directory. Thin wrapper around the `sync_dir` function.

        Args:
            dir: Directory with wandb files to be synced
        """
        sync_dir(dir, options=self.wandb_options, timeout=self._timeout)

    def loop(self) -> None:
        """Read command files and trigger syncing"""
        logger.info(
            "wandb-osh v%s, starting to watch %s", __version__, self.command_dir
        )
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                start_time = time.time()
                self.command_dir.mkdir(parents=True, exist_ok=True)
                self._collect_done()
                command_files = []
                targets = []
                for command_file in self.command_dir.glob("*.command"):
                    try:
                        target = Path(command_file.read_text())
                    except FileNotFoundError:
                        # File was removed between glob and read_text by another process.
                        continue
                    command_files.append(command_file)
                    if not target.is_dir():
                        logger.error(
                            "Command file %s points to non-existing directory %s",
                            command_file,
                            target,
                        )
                        continue
                    targets.append(target)
                self._pending.update(targets)
                self._schedule(executor)
                time.sleep(0.25)
                for cf in command_files:
                    try:
                        if cf.is_file():
                            cf.unlink()
                    except FileNotFoundError:
                        # Another process may have already removed it.
                        pass
                if "PYTEST_CURRENT_TEST" in os.environ:
                    self._wait_for_all()
                    break
                time.sleep(max(0.0, (time.time() - start_time) - self.wait))

    def _schedule(self, executor: ThreadPoolExecutor) -> None:
        available = self.max_workers - len(self._in_progress)
        if available <= 0 or not self._pending:
            return
        for target in list(self._pending):
            if available <= 0:
                break
            self._pending.remove(target)
            logger.info("Syncing %s...", target)
            future = executor.submit(self.sync, target)
            self._in_progress[future] = target
            available -= 1

    def _collect_done(self) -> None:
        done_futures = [f for f in self._in_progress if f.done()]
        for future in done_futures:
            target = self._in_progress.pop(future)
            try:
                future.result()
            except subprocess.TimeoutExpired:
                # try again later
                logger.warning("Syncing %s timed out. Trying later.", target)
                self._requeue(target)

    def _requeue(self, target: PathLike) -> None:
        from wandb_osh.hooks import TriggerWandbSyncHook

        TriggerWandbSyncHook(self.command_dir)(target)
        self._pending.add(Path(target))

    def _wait_for_all(self) -> None:
        if not self._in_progress:
            return
        wait(self._in_progress.keys())
        self._collect_done()


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
