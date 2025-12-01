#!/usr/bin/env python3
"""
Claude Zones - Context detector for Claude Code

Detects the current project zone based on filesystem path and returns
appropriate behavioral configuration.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Default zone definitions - customize these paths
DEFAULT_ZONES = {
    "career": {
        "paths": [
            "~/Desktop/1_PRIORITY_JOB_SEARCH",
            "~/Documents/Career",
            "~/Projects/*job*",
            "~/Projects/*resume*",
        ],
        "config": "zones/career.md"
    },
    "finance": {
        "paths": [
            "~/Documents/Finance",
            "~/Projects/*budget*",
            "~/Projects/*tax*",
        ],
        "config": "zones/finance.md"
    },
    "development": {
        "paths": [
            "~/Projects",
            "~/Code",
            "~/Developer",
        ],
        "config": "zones/development.md"
    },
    "research": {
        "paths": [
            "~/Documents/Research",
            "~/Projects/*research*",
            "~/Projects/*analysis*",
        ],
        "config": "zones/research.md"
    }
}


def expand_path(path: str) -> str:
    """Expand ~ and environment variables in path."""
    return os.path.expanduser(os.path.expandvars(path))


def path_matches(current: Path, pattern: str) -> bool:
    """Check if current path matches a zone pattern (supports * wildcards)."""
    pattern_expanded = expand_path(pattern)

    # Handle wildcards
    if "*" in pattern_expanded:
        import fnmatch
        pattern_parts = Path(pattern_expanded).parts
        current_parts = current.parts

        if len(current_parts) < len(pattern_parts):
            return False

        for i, pattern_part in enumerate(pattern_parts):
            if i >= len(current_parts):
                return False
            if not fnmatch.fnmatch(current_parts[i].lower(), pattern_part.lower()):
                return False
        return True
    else:
        pattern_path = Path(pattern_expanded)
        try:
            current.relative_to(pattern_path)
            return True
        except ValueError:
            return False


def detect_zone(path: Optional[str] = None, zones: Optional[dict] = None) -> dict:
    """
    Detect which zone the given path belongs to.

    Args:
        path: Directory path to check. Defaults to current working directory.
        zones: Zone definitions dict. Defaults to DEFAULT_ZONES.

    Returns:
        dict with 'zone' name, 'config' path, and 'matched_pattern'
    """
    if path is None:
        path = os.getcwd()

    if zones is None:
        zones = DEFAULT_ZONES

    current = Path(path).resolve()

    # Check zones in order (more specific patterns should be listed first in config)
    for zone_name, zone_config in zones.items():
        for pattern in zone_config["paths"]:
            if path_matches(current, pattern):
                return {
                    "zone": zone_name,
                    "config": zone_config["config"],
                    "matched_pattern": pattern,
                    "path": str(current)
                }

    # Default fallback
    return {
        "zone": "default",
        "config": "zones/default.md",
        "matched_pattern": None,
        "path": str(current)
    }


def load_zone_config(config_path: str) -> str:
    """Load the zone configuration file content."""
    # Look for config relative to this script's location
    script_dir = Path(__file__).parent
    full_path = script_dir / config_path

    if full_path.exists():
        return full_path.read_text()

    # Also check ~/.claude/zones/
    user_path = Path.home() / ".claude" / config_path
    if user_path.exists():
        return user_path.read_text()

    return f"# Zone config not found: {config_path}"


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect Claude Code zone based on current directory"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=os.getcwd(),
        help="Path to check (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Output the zone's configuration content"
    )
    parser.add_argument(
        "--zone-only",
        action="store_true",
        help="Output only the zone name"
    )

    args = parser.parse_args()

    result = detect_zone(args.path)

    if args.zone_only:
        print(result["zone"])
    elif args.config:
        print(load_zone_config(result["config"]))
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Zone: {result['zone']}")
        print(f"Config: {result['config']}")
        if result['matched_pattern']:
            print(f"Matched: {result['matched_pattern']}")


if __name__ == "__main__":
    main()
