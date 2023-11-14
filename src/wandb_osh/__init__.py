from __future__ import annotations

try:
    from importlib.metadata import version
except ModuleNotFoundError:
    from importlib_metadata import version  # type: ignore

__version__ = version("wandb_osh")


from wandb_osh.util.log import set_log_level


__all__ = ["__version__", "set_log_level"]
