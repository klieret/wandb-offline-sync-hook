from __future__ import annotations

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version  # type: ignore

__version__ = version("wandb_osh")
