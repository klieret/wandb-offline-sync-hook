from __future__ import annotations

from os import PathLike
from pathlib import Path

from ray.tune.experiment.trial import Trial
from ray.tune.logger import LoggerCallback

from wandb_osh.hooks import TriggerWandbSyncHook

_comm_default_dir = Path("~/.wandb_osh_command_dir").expanduser()


class TriggerWandbSyncRayHook(LoggerCallback):
    def __init__(
        self,
        communication_dir: PathLike = _comm_default_dir,
        sync_every_n_epochs: int = 1,
    ):
        """Hook to be used when interfacing wandb with ray tune.

        Args:
            communication_dir: Directory used for communication with wandb-osh.
            sync_every_n_epochs: Number of epochs between each trigger (default = 1, every epoch).
        """
        super().__init__()
        self._hook = TriggerWandbSyncHook(
            communication_dir=communication_dir, sync_every_n_epochs=sync_every_n_epochs
        )

    def log_trial_result(self, iteration: int, trial: Trial, result: dict):
        trial_dir = Path(trial.logdir)
        self._hook(trial_dir, current_epoch=iteration)
