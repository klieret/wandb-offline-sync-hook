from __future__ import annotations

import logging

from wandb_osh.cli import main


def test_cli(tmp_path, caplog):
    with caplog.at_level(logging.INFO):
        main(argv=["--command-dir", str(tmp_path)])
    assert "Starting to watch" in caplog.text
    target = tmp_path / "test" / "123"
    target.mkdir(parents=True)
    (tmp_path / "123.command").write_text(f"{tmp_path}/test/123")
    with caplog.at_level(logging.INFO):
        main(argv=["--command-dir", str(tmp_path)])
    assert f"Syncing {target}" in caplog.text
