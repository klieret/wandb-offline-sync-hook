from __future__ import annotations

from os import PathLike

from wandb_osh.hooks import TriggerWandbSyncHook, _comm_default_dir
from wandb_osh.util.log import logger


# See #96
# Possible additional issues: If both imports are working, the wrong one might be used.
try:
    # This is the modern way
    import lightning.pytorch as pl
except ImportError:
    import pytorch_lightning as pl

    logger.warning(
        "Imported lightning the legacy way (import pytorch_lightning as pl). "
        "For more information see https://github.com/klieret/wandb-offline-sync-hook/issues/96"
    )


class TriggerWandbSyncLightningCallback(pl.Callback):
    def __init__(
        self,
        communication_dir: PathLike = _comm_default_dir,
    ):
        """Hook to be used when interfacing wandb with Lightning.

        Args:
            communication_dir: Directory used for communication with wandb-osh.

        Usage

        .. code-block:: python

            from wandb_osh.lightning_hooks import TriggerWandbSyncLightningCallback

            trainer = Trainer(callbacks=[TriggerWandbSyncLightningCallback()])

        """
        super().__init__()
        self._hook = TriggerWandbSyncHook(communication_dir=communication_dir)

    def on_validation_epoch_end(
        self,
        trainer: pl.Trainer,
        pl_module: pl.LightningModule,
    ) -> None:
        if trainer.sanity_checking:
            return
        self._hook()
