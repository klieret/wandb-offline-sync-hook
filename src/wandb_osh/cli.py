from __future__ import annotations

import subprocess
import time
from os import PathLike
from pathlib import Path

import click
from gnn_tracking.utils.log import logger

_command_dir_default = Path("~/.wandb_osh_command_dir").expanduser()


def sync_dir(dir: PathLike):
    """Call wandb sync on a directory."""
    dir = Path(dir)
    subprocess.run(["wandb", "sync", "--sync-all"], cwd=dir)


class WandbOSH:
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
            self.command_dir.mkdir(parents=True, exist_ok=True)
            start_time = time.time()
            for command_file in self.command_dir.glob("*.command"):
                self._handle_command_file(command_file)
            time.sleep(max(0.0, (time.time() - start_time) - self.wait))


@click.command()
@click.option(
    "--command-dir",
    default=_command_dir_default,
    type=click.Path(exists=True, file_okay=False),
    show_default=True,
)
@click.option("--wait", default=1, show_default=True)
def main(command_dir: PathLike = _command_dir_default, wait: int = 1) -> None:
    """Main loop

    Args:
        command_dir: Directory to look for command files
        wait:  How much to wait between syncings?

    Returns:
        None
    """
    wandb_osh = WandbOSH(command_dir=command_dir, wait=wait)
    wandb_osh.loop()


if __name__ == "__main__":
    main()
