from __future__ import annotations

import logging
import subprocess
import unittest
import unittest.mock
from pathlib import Path

from wandb_osh.syncer import WandbSyncer
from wandb_osh.util.log import set_log_level


def test_wandb_syncer(tmp_path, caplog):
    set_log_level("DEBUG")
    tmp_path = Path(tmp_path)
    ws = WandbSyncer(tmp_path)
    target = tmp_path / "test" / "123"
    (tmp_path / "123.command").write_text(str(target.resolve()))
    with caplog.at_level(logging.WARNING):
        ws.loop()
    assert "points to non-existing directory" in caplog.text
    caplog.clear()
    (tmp_path / "123.command").write_text(str(target.resolve()))
    target.mkdir(parents=True)
    with caplog.at_level(logging.DEBUG):
        ws.loop()
    assert f"Command would be: wandb sync . in {target.resolve()}" in caplog.text
    set_log_level()


def test_wandb_sync_timeout(tmp_path, caplog):
    with unittest.mock.patch(
        "wandb_osh.syncer.sync_dir", side_effect=subprocess.TimeoutExpired("asdf", 123)
    ):
        tmp_path = Path(tmp_path)
        ws = WandbSyncer(tmp_path)
        target = tmp_path / "test" / "123"
        (tmp_path / "123.command").write_text(str(target.resolve()))
        target.mkdir(parents=True)
        with caplog.at_level(logging.DEBUG):
            ws.loop()
        assert "timed out. Trying later." in caplog.text
