from __future__ import annotations

from os import PathLike
from pathlib import Path

import wandb

from wandb_osh import __version__
from wandb_osh.util.hash_id import hash_id
from wandb_osh.util.log import logger

_comm_default_dir = Path("~/.wandb_osh_command_dir").expanduser()


class TriggerWandbSyncHook:
    def __init__(self, communication_dir: PathLike = _comm_default_dir):
        """Hook to trigger synchronization of wandb with wandb-osh

        Args:
            communication_dir: Directory used for communication with wandb-osh.
        """
        self.communication_dir = Path(communication_dir)
        self.communication_dir.mkdir(parents=True, exist_ok=True)
        logger.info(
            "This is wandb-osh v%s using communication directory %s",
            __version__,
            self.communication_dir,
        )

    def __call__(self, logdir: str | PathLike | None = None):
        """Trigger synchronization on the head nodes

        Args:
            logdir: The directory in which wandb puts its run files.

        Returns:
            None
        """
        if logdir is None:
            # run.dir actually points to the `/files` subdirectory of the run,
            # but we need the directory above that.
            logdir = Path(wandb.run.dir).parent.resolve()
        trial_dir = Path(logdir).resolve()
        cmd_fname = hash_id(str(trial_dir)) + ".command"
        # In case the communication dir was deleted since we initialized this class
        self.communication_dir.mkdir(parents=True, exist_ok=True)
        command_file = self.communication_dir / cmd_fname
        if command_file.is_file():
            logger.warning(
                "Syncing not active or too slow: Command %s file still exists",
                command_file,
            )
        command_file.touch(exist_ok=True)
        command_file.write_text(trial_dir.resolve().as_posix())
        logger.debug("Wrote command file %s", command_file)
