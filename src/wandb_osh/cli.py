from __future__ import annotations

from argparse import ArgumentParser

from wandb_osh.config import _command_dir_default
from wandb_osh.syncer import WandbSyncer


def main() -> None:
    parser = ArgumentParser(description="Wandb offline syncer.")
    parser.add_argument(
        "--command-dir",
        default=_command_dir_default,
        help="Command dir: Directory in which the hook creates files to trigger a "
        "synchronization.",
    )
    parser.add_argument(
        "--wait",
        default=_command_dir_default,
        help="Minimal time that has to pass before checking the command dir again.",
    )
    args = parser.parse_args()
    wandb_osh = WandbSyncer(command_dir=args.command_dir, wait=args.wait)
    wandb_osh.loop()


if __name__ == "__main__":
    main()
