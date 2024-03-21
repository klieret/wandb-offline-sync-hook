from __future__ import annotations

from unittest.mock import Mock

import pytest
import wandb

_ray = pytest.importorskip("lightning")

from wandb_osh.lightning_hooks import TriggerWandbSyncLightningCallback  # noqa: E402


def test_manual_trigger(tmp_path):
    wandb.init(project="test", mode="offline", dir=tmp_path)
    lh = TriggerWandbSyncLightningCallback(tmp_path)
    trainer = Mock()
    trainer.sanity_checking = False
    module = Mock()
    lh.on_validation_epoch_end(trainer, module)  # type: ignore
    assert len([f for f in tmp_path.iterdir() if f.suffix == ".command"]) == 1
