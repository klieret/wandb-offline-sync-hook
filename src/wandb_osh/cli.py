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
    command_dir = Path(command_dir)
    logger.info("Starting to watch %s", command_dir)
    showed_nexist_warning = False
    while True:
        if not command_dir.is_dir():
            if not showed_nexist_warning:
                logger.warning(
                    "Command dir %s does not yet exist. Skipping. Either no trial has "
                    "completed yet, or you do not use the same directory for your "
                    "hook.",
                    command_dir,
                )
                showed_nexist_warning = True
            time.sleep(wait)
            continue

        start_time = time.time()
        for command_file in command_dir.glob("*.command"):
            dir = Path(command_file.read_text())
            if not dir.is_dir():
                logger.error(
                    "Command file %s points to non-existing directory %s",
                    command_file,
                    dir,
                )
                continue
            logger.info("Syncing %s...", dir)
            sync_dir(dir)
            logger.info("Syncing Done")
            command_file.unlink()

        time.sleep(max(0.0, (time.time() - start_time) - wait))


if __name__ == "__main__":
    main()
