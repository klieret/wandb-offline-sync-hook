from __future__ import annotations

import logging

from wandb_osh.hooks import TriggerWandbSyncHook


def test_trigger_wandb_sync_hook(tmp_path, caplog):
    hook = TriggerWandbSyncHook(tmp_path, warn_if_inactive=True)
    hook("/test/123")
    assert (tmp_path / "d2d46f.command").is_file()
    assert (tmp_path / "d2d46f.command").read_text() == "/test/123"
    with caplog.at_level(logging.WARNING):
        hook("/test/123")
    assert "Syncing not active or too slow" in caplog.text

def test_trigger_wandb_sync_hook_no_warn_if_inactive(tmp_path, caplog):
    hook = TriggerWandbSyncHook(tmp_path, warn_if_inactive=False)
    hook("/test/123")
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="wandb_osh"):
        hook("/test/123")
    assert "Syncing not active or too slow" not in caplog.text
