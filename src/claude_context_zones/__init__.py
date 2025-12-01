"""
Claude Context Zones - Context-aware behavior switching for Claude Code

Detects your working directory and loads context-appropriate behavioral
instructions automatically.

Features:
- Path-based zone detection with wildcards
- Zone inheritance/composition
- Project-level overrides via .claude-zone file
- Usage metrics tracking
- Parallel development support
- MCP server for dynamic zone switching
"""

from .detector import (
    detect_zone,
    load_zone_config,
    load_inherited_config,
    get_zone_metrics,
    log_zone_usage,
    load_user_zones,
    merge_zones,
    init_user_config,
    generate_hook_script,
    DEFAULT_ZONES,
)

__version__ = "1.1.0"
__all__ = [
    "detect_zone",
    "load_zone_config",
    "load_inherited_config",
    "get_zone_metrics",
    "log_zone_usage",
    "load_user_zones",
    "merge_zones",
    "init_user_config",
    "generate_hook_script",
    "DEFAULT_ZONES",
]
