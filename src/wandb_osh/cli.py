from __future__ import annotations

from os import PathLike

import click

from wandb_osh.config import _command_dir_default
from wandb_osh.syncer import WandbSyncer


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
    wandb_osh = WandbSyncer(command_dir=command_dir, wait=wait)
    wandb_osh.loop()


if __name__ == "__main__":
    main()
