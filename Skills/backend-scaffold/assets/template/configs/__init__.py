"""Configs package — re-exports the common entry points used by main.py."""
from configs.settings import settings
from configs.lifespan import lifespan

__all__ = ["settings", "lifespan"]
