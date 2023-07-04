from __future__ import annotations

import wandb

from wandb_osh.lightning_hooks import TriggerWandbSyncLightningCallback


def test_manual_trigger(tmp_path):
    wandb.init(project="test", mode="offline", dir=tmp_path)
    lh = TriggerWandbSyncLightningCallback(tmp_path)
    lh.on_validation_epoch_end(None, None)  # type: ignore
    assert len([f for f in tmp_path.iterdir() if f.suffix == ".command"]) == 1
