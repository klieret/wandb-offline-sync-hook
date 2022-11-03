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
    subprocess.run(["wandb", "sync", "--sync-all", dir.resolve()])


@click.command()
@click.option(
    "--command-dir",
    default=_command_dir_default,
    type=click.Path(exists=True, file_okay=False),
    show_default=True,
)
@click.option("--wait", default=10, show_default=True)
def main(command_dir: PathLike = _command_dir_default, wait: int = 10) -> None:
    """Main loop

    Args:
        command_dir: Directory to look for command files
        wait:  How much to wait between syncings?

    Returns:
        None
    """
    command_dir = Path(command_dir)
    while True:
        if not command_dir.is_dir():
            logger.warning("Command dir %s does not yet exist. Skipping. ", command_dir)
            time.sleep(wait)
            continue

        for command_file in command_dir.glob("*.command"):
            dir = Path(command_file.read_text())
            if not dir.is_dir():
                logger.error(
                    "Command file %s points to non-existing directory %s",
                    command_file,
                    dir,
                )
                continue
            logger.info("Syncing %s", dir)
            sync_dir(dir)
            logger.info("Finished syncing %s", dir)
            command_file.unlink()

        time.sleep(wait)


if __name__ == "__main__":
    main()
