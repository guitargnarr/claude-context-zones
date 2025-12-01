"""
Claude Context Zones - Context-aware behavior switching for Claude Code

Detects your working directory and loads context-appropriate behavioral
instructions automatically.
"""

from .detector import detect_zone, load_zone_config, DEFAULT_ZONES

__version__ = "1.0.0"
__all__ = ["detect_zone", "load_zone_config", "DEFAULT_ZONES"]
