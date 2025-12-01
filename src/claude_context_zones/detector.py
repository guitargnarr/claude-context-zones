#!/usr/bin/env python3
"""
Claude Zones - Context detector for Claude Code

Detects the current project zone based on filesystem path and returns
appropriate behavioral configuration.

Features:
- Path-based zone detection with wildcards
- Zone inheritance/composition
- Project-level overrides via .claude-zone file
- Usage metrics tracking
- Parallel development support
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Set
from datetime import datetime

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
    },
    "parallel": {
        "paths": [
            "~/Projects/.worktrees/*",
            "*/.worktrees/*",
        ],
        "inherits": ["development"],
        "config": "zones/parallel.md"
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


def check_project_override(path: Path) -> Optional[str]:
    """
    Check for .claude-zone file in project root or parents.

    Returns the zone name if found, None otherwise.
    """
    current = path
    for _ in range(10):  # Limit search depth
        zone_file = current / ".claude-zone"
        if zone_file.exists():
            content = zone_file.read_text().strip()
            # First line is zone name, rest is ignored (can be comments)
            zone_name = content.split('\n')[0].strip()
            if zone_name and not zone_name.startswith('#'):
                return zone_name

        # Also check for .git to stop at repo root
        if (current / ".git").exists():
            break

        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def load_user_zones() -> Dict:
    """Load user-defined zones from ~/.claude/zones.json if it exists."""
    user_zones_path = Path.home() / ".claude" / "zones.json"
    if user_zones_path.exists():
        try:
            return json.loads(user_zones_path.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def merge_zones(base: Dict, user: Dict) -> Dict:
    """Merge user zones with default zones (user takes precedence)."""
    merged = dict(base)
    merged.update(user)
    return merged


def resolve_inheritance(zone_name: str, zones: Dict, visited: Optional[Set[str]] = None) -> List[str]:
    """
    Resolve zone inheritance chain.

    Returns list of zone names in order (most specific first).
    Handles circular references.
    """
    if visited is None:
        visited = set()

    if zone_name in visited:
        return []  # Circular reference

    visited.add(zone_name)
    result = [zone_name]

    zone_config = zones.get(zone_name, {})
    inherits = zone_config.get("inherits", [])

    if isinstance(inherits, str):
        inherits = [inherits]

    for parent in inherits:
        if parent in zones:
            result.extend(resolve_inheritance(parent, zones, visited))

    return result


def log_zone_usage(zone_name: str, path: str) -> None:
    """
    Log zone detection for usage metrics.

    Logs to ~/.claude/zone-history.log
    """
    log_path = Path.home() / ".claude" / "zone-history.log"

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp}\t{zone_name}\t{path}\n"

        with open(log_path, "a") as f:
            f.write(log_entry)
    except (OSError, IOError):
        pass  # Silent fail for logging


def get_zone_metrics() -> Dict:
    """
    Get zone usage metrics from history log.

    Returns dict with zone counts, most recent, etc.
    """
    log_path = Path.home() / ".claude" / "zone-history.log"

    if not log_path.exists():
        return {"total": 0, "zones": {}, "recent": []}

    try:
        lines = log_path.read_text().strip().split('\n')
        zone_counts: Dict[str, int] = {}
        recent = []

        for line in lines[-1000:]:  # Last 1000 entries
            parts = line.split('\t')
            if len(parts) >= 2:
                zone = parts[1]
                zone_counts[zone] = zone_counts.get(zone, 0) + 1

        # Get last 10 for recent
        for line in lines[-10:]:
            parts = line.split('\t')
            if len(parts) >= 3:
                recent.append({
                    "timestamp": parts[0],
                    "zone": parts[1],
                    "path": parts[2]
                })

        return {
            "total": len(lines),
            "zones": zone_counts,
            "recent": list(reversed(recent))
        }
    except (OSError, IOError):
        return {"total": 0, "zones": {}, "recent": []}


def detect_zone(path: Optional[str] = None, zones: Optional[dict] = None,
                log: bool = False) -> dict:
    """
    Detect which zone the given path belongs to.

    Args:
        path: Directory path to check. Defaults to current working directory.
        zones: Zone definitions dict. Defaults to merged DEFAULT_ZONES + user zones.
        log: Whether to log this detection for metrics.

    Returns:
        dict with 'zone' name, 'config' path, 'matched_pattern', 'inheritance'
    """
    if path is None:
        path = os.getcwd()

    if zones is None:
        user_zones = load_user_zones()
        zones = merge_zones(DEFAULT_ZONES, user_zones)

    current = Path(path).resolve()

    # First check for project-level override
    override = check_project_override(current)
    if override and override in zones:
        inheritance = resolve_inheritance(override, zones)
        result = {
            "zone": override,
            "config": zones[override].get("config", f"zones/{override}.md"),
            "matched_pattern": ".claude-zone override",
            "path": str(current),
            "inheritance": inheritance,
            "override": True
        }
        if log:
            log_zone_usage(override, str(current))
        return result

    # Check zones in order (more specific patterns should be listed first in config)
    for zone_name, zone_config in zones.items():
        for pattern in zone_config.get("paths", []):
            if path_matches(current, pattern):
                inheritance = resolve_inheritance(zone_name, zones)
                result = {
                    "zone": zone_name,
                    "config": zone_config.get("config", f"zones/{zone_name}.md"),
                    "matched_pattern": pattern,
                    "path": str(current),
                    "inheritance": inheritance,
                    "override": False
                }
                if log:
                    log_zone_usage(zone_name, str(current))
                return result

    # Default fallback
    result = {
        "zone": "default",
        "config": "zones/default.md",
        "matched_pattern": None,
        "path": str(current),
        "inheritance": ["default"],
        "override": False
    }
    if log:
        log_zone_usage("default", str(current))
    return result


def load_zone_config(config_path: str, zones: Optional[Dict] = None) -> str:
    """
    Load the zone configuration file content.

    Supports inheritance - loads and merges parent zone configs.
    """
    # Look for config relative to this script's location
    script_dir = Path(__file__).parent
    full_path = script_dir / config_path

    content_parts = []

    if full_path.exists():
        content_parts.append(full_path.read_text())
    else:
        # Also check ~/.claude/zones/
        user_path = Path.home() / ".claude" / config_path
        if user_path.exists():
            content_parts.append(user_path.read_text())
        else:
            content_parts.append(f"# Zone config not found: {config_path}")

    return "\n".join(content_parts)


def load_inherited_config(zone_name: str, zones: Optional[Dict] = None) -> str:
    """
    Load zone config with all inherited parent configs merged.

    Returns combined config with most specific first.
    """
    if zones is None:
        user_zones = load_user_zones()
        zones = merge_zones(DEFAULT_ZONES, user_zones)

    inheritance = resolve_inheritance(zone_name, zones)

    content_parts = []
    for inherited_zone in inheritance:
        zone_config = zones.get(inherited_zone, {})
        config_path = zone_config.get("config", f"zones/{inherited_zone}.md")

        # Load the config
        script_dir = Path(__file__).parent
        full_path = script_dir / config_path

        if full_path.exists():
            content_parts.append(f"# === Zone: {inherited_zone} ===\n")
            content_parts.append(full_path.read_text())
            content_parts.append("\n")
        else:
            user_path = Path.home() / ".claude" / config_path
            if user_path.exists():
                content_parts.append(f"# === Zone: {inherited_zone} ===\n")
                content_parts.append(user_path.read_text())
                content_parts.append("\n")

    if not content_parts:
        return f"# No config found for zone: {zone_name}"

    return "\n".join(content_parts)


def generate_hook_script() -> str:
    """Generate a hook script for automatic zone loading."""
    return '''#!/bin/bash
# Claude Code Hook: Automatic Zone Loading
# Install: cp this to ~/.claude/hooks/session-start.sh && chmod +x ~/.claude/hooks/session-start.sh

# Detect current zone and output config
if command -v claude-zones &> /dev/null; then
    echo "# Zone Context"
    echo "# Current zone: $(claude-zones --zone-only)"
    echo ""
    claude-zones --config --with-inheritance
fi
'''


def init_user_config() -> str:
    """
    Initialize user configuration in ~/.claude/zones/.

    Creates example zones.json and zone markdown files.
    """
    claude_dir = Path.home() / ".claude"
    zones_dir = claude_dir / "zones"

    # Create directories
    zones_dir.mkdir(parents=True, exist_ok=True)

    created = []

    # Create zones.json if not exists
    zones_json = claude_dir / "zones.json"
    if not zones_json.exists():
        example_config = {
            "career": {
                "paths": ["~/Desktop/Job-Search", "~/Projects/*resume*"],
                "config": "zones/career.md"
            },
            "finance": {
                "paths": ["~/Documents/Finance"],
                "config": "zones/finance.md"
            },
            "development": {
                "paths": ["~/Projects", "~/Code"],
                "config": "zones/development.md"
            },
            "research": {
                "paths": ["~/Documents/Research"],
                "config": "zones/research.md"
            }
        }
        zones_json.write_text(json.dumps(example_config, indent=2))
        created.append(str(zones_json))

    # Create hook directory and example
    hooks_dir = claude_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_file = hooks_dir / "session-start.sh.example"
    if not hook_file.exists():
        hook_file.write_text(generate_hook_script())
        created.append(str(hook_file))

    return f"Initialized: {', '.join(created)}" if created else "Already initialized"


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect Claude Code zone based on current directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude-zones                    # Detect zone for current directory
  claude-zones ~/Projects/myapp   # Check specific path
  claude-zones --config           # Output zone's behavioral instructions
  claude-zones --with-inheritance # Include inherited zone configs
  claude-zones --metrics          # Show usage statistics
  claude-zones --init             # Initialize user config
  claude-zones --hook             # Output hook script for auto-loading
"""
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
        "--with-inheritance",
        action="store_true",
        help="Include inherited zone configs (use with --config)"
    )
    parser.add_argument(
        "--zone-only",
        action="store_true",
        help="Output only the zone name"
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Log this detection for usage metrics"
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Show zone usage metrics"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize user configuration in ~/.claude/"
    )
    parser.add_argument(
        "--hook",
        action="store_true",
        help="Output hook script for automatic zone loading"
    )
    parser.add_argument(
        "--list-zones",
        action="store_true",
        help="List all available zones"
    )

    args = parser.parse_args()

    # Handle special commands first
    if args.init:
        print(init_user_config())
        return

    if args.hook:
        print(generate_hook_script())
        return

    if args.metrics:
        metrics = get_zone_metrics()
        if args.json:
            print(json.dumps(metrics, indent=2))
        else:
            print(f"Total detections: {metrics['total']}")
            print("\nZone usage counts:")
            for zone, count in sorted(metrics['zones'].items(), key=lambda x: -x[1]):
                print(f"  {zone}: {count}")
            if metrics['recent']:
                print("\nRecent:")
                for entry in metrics['recent'][:5]:
                    print(f"  {entry['zone']} - {entry['path']}")
        return

    if args.list_zones:
        user_zones = load_user_zones()
        zones = merge_zones(DEFAULT_ZONES, user_zones)
        if args.json:
            print(json.dumps(list(zones.keys())))
        else:
            print("Available zones:")
            for zone_name, zone_config in zones.items():
                inherits = zone_config.get("inherits", [])
                inherit_str = f" (inherits: {', '.join(inherits)})" if inherits else ""
                print(f"  {zone_name}{inherit_str}")
        return

    result = detect_zone(args.path, log=args.log)

    if args.zone_only:
        print(result["zone"])
    elif args.config:
        if args.with_inheritance:
            print(load_inherited_config(result["zone"]))
        else:
            print(load_zone_config(result["config"]))
    elif args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Zone: {result['zone']}")
        print(f"Config: {result['config']}")
        if result['matched_pattern']:
            print(f"Matched: {result['matched_pattern']}")
        if len(result.get('inheritance', [])) > 1:
            print(f"Inherits: {' → '.join(result['inheritance'])}")
        if result.get('override'):
            print("(via .claude-zone override)")


if __name__ == "__main__":
    main()
