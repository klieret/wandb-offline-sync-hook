from __future__ import annotations

import logging

import pytest

_ray = pytest.importorskip("ray")
from wandb_osh.ray_hooks import TriggerWandbSyncRayHook  # noqa: E402


class MockTrial:
    def __init__(self, logdir):
        self.logdir = logdir


def test_trigger_wandb_sync_hook(tmp_path, caplog):
    hook = TriggerWandbSyncRayHook(tmp_path, warn_if_inactive=True)

    trial = MockTrial(logdir="/test/123")

    hook.log_trial_result(0, trial, {})  # type: ignore
    assert (tmp_path / "d2d46f.command").is_file()
    assert (tmp_path / "d2d46f.command").read_text() == "/test/123"
    with caplog.at_level(logging.WARNING):
        hook.log_trial_result(0, trial, {})  # type: ignore
    assert "Syncing not active or too slow" in caplog.text

def test_trigger_wandb_sync_ray_hook_no_warn_if_inactive(tmp_path, caplog):
    hook = TriggerWandbSyncRayHook(tmp_path, warn_if_inactive=False)
    trial = MockTrial(logdir="/test/123")
    hook.log_trial_result(0, trial, {})  # creates file
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="wandb_osh"):
        hook.log_trial_result(0, trial, {})
    assert "Syncing not active or too slow" not in caplog.text
