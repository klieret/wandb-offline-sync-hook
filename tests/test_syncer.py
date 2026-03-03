from __future__ import annotations

import logging
import subprocess
import threading
import unittest
import unittest.mock
from os import PathLike
from pathlib import Path

import pytest

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


def test_wandb_syncer_max_workers_concurrent(tmp_path):
    tmp_path = Path(tmp_path)
    started = []
    lock = threading.Lock()
    started_two = threading.Event()
    release = threading.Event()

    def slow_sync(target):
        with lock:
            started.append(target)
            if len(started) >= 2:
                started_two.set()
        release.wait(timeout=2)

    class _TestSyncer(WandbSyncer):
        def sync(self, dir: PathLike) -> None:
            slow_sync(dir)

    ws = _TestSyncer(tmp_path, max_workers=2, wait=0)

    for i in range(3):
        target = tmp_path / f"run{i}"
        target.mkdir(parents=True)
        (tmp_path / f"{i}.command").write_text(str(target.resolve()))

    thread = threading.Thread(target=ws.loop, daemon=True)
    thread.start()
    assert started_two.wait(timeout=2)
    with lock:
        assert len(started) == 2
    release.set()
    thread.join(timeout=2)
    assert not thread.is_alive()


def test_wandb_syncer_invalid_max_workers(tmp_path):
    with pytest.raises(ValueError):
        WandbSyncer(tmp_path, max_workers=0)
