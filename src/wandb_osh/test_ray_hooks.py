from __future__ import annotations

import logging

import pytest

_ray = pytest.importorskip("ray")
from wandb_osh.ray_hooks import TriggerWandbSyncRayHook  # noqa: E402


class MockTrial:
    def __init__(self, logdir):
        self.logdir = logdir


def test_trigger_wandb_sync_hook(tmp_path, caplog):
    hook = TriggerWandbSyncRayHook(tmp_path)

    trial = MockTrial(logdir="/test/123")

    hook.log_trial_result(0, trial, {})  # type: ignore
    assert (tmp_path / "d2d46f.command").is_file()
    assert (tmp_path / "d2d46f.command").read_text() == "/test/123"
    with caplog.at_level(logging.WARNING):
        hook.log_trial_result(0, trial, {})  # type: ignore
    assert "Syncing not active or too slow" in caplog.text
