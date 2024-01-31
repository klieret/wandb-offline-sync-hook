from __future__ import annotations

from argparse import ArgumentParser

from wandb_osh.config import _command_dir_default
from wandb_osh.syncer import WandbSyncer


def _get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Wandb offline syncer. To pass arguments to wandb sync, e.g., "
        "`--sync-all`, use `--` before the arguments. For example: "
        "`wandb-osh --wait 10 -- --sync-all`"
    )
    parser.add_argument(
        "--command-dir",
        default=_command_dir_default,
        help="Command dir: Directory in which the hook creates files to trigger a "
        "synchronization.",
    )
    parser.add_argument(
        "--wait",
        default=1,
        type=float,
        help="Minimal time that has to pass before checking the command dir again.",
    )
    parser.add_argument(
        "--timeout",
        default=120,
        type=int,
        help="Timeout for wandb sync. If <=0, no timeout.",
    )
    parser.add_argument(
        "--num-workers",
        default=1,
        type=int,
        help="Number of parallel syncs to run at a time.",
    )
    parser.add_argument(
        "wandb_options",
        nargs="*",
        help="Options to be passed on to `wandb sync`, e.g. `--sync-all`. When "
        "specifying a flag to wandb, please add a `--` before the option, "
        "e.g., `wandb-osh -- --sync-all`",
    )
    return parser


def main(argv=None) -> None:
    parser = _get_parser()
    args = parser.parse_args(argv)
    wandb_osh = WandbSyncer(
        command_dir=args.command_dir,
        wait=args.wait,
        wandb_options=args.wandb_options,
        num_workers=args.num_workers,
    )
    wandb_osh.start()


if __name__ == "__main__":
    main()
