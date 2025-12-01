#!/bin/bash
#
# Claude Zones - Installation Script
#
# Installs zone detection and configuration files for Claude Code
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
ZONES_DIR="$CLAUDE_DIR/zones"

echo "Claude Zones Installer"
echo "======================"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$ZONES_DIR"

# Copy zone configurations
echo "Installing zone configurations..."
cp -r "$SCRIPT_DIR/zones/"* "$ZONES_DIR/"

# Copy detector script
echo "Installing detector..."
cp "$SCRIPT_DIR/detector.py" "$CLAUDE_DIR/detector.py"
chmod +x "$CLAUDE_DIR/detector.py"

# Create zones.json config if it doesn't exist
CONFIG_FILE="$CLAUDE_DIR/zones.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default zones.json..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "career": {
    "paths": [
      "~/Desktop/1_PRIORITY_JOB_SEARCH",
      "~/Documents/Career",
      "~/Projects/*job*",
      "~/Projects/*resume*"
    ],
    "config": "zones/career.md"
  },
  "finance": {
    "paths": [
      "~/Documents/Finance",
      "~/Projects/*budget*",
      "~/Projects/*tax*"
    ],
    "config": "zones/finance.md"
  },
  "development": {
    "paths": [
      "~/Projects",
      "~/Code",
      "~/Developer"
    ],
    "config": "zones/development.md"
  },
  "research": {
    "paths": [
      "~/Documents/Research",
      "~/Projects/*research*",
      "~/Projects/*analysis*"
    ],
    "config": "zones/research.md"
  }
}
EOF
else
    echo "zones.json already exists, skipping..."
fi

# Add to CLAUDE.md if not present
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
ZONE_SNIPPET='@~/.claude/zones/${ZONE}.md'

if [ -f "$CLAUDE_MD" ]; then
    if ! grep -q "claude-zones" "$CLAUDE_MD"; then
        echo ""
        echo "Add this to your CLAUDE.md to enable zone-based behaviors:"
        echo ""
        echo "  # Zone-Based Behavior (claude-zones)"
        echo "  # Load zone config: \$(~/.claude/detector.py --zone-only)"
        echo "  @~/.claude/zones/\$(~/.claude/detector.py --zone-only).md"
        echo ""
    fi
else
    echo "No CLAUDE.md found. Create one at $CLAUDE_MD"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  ~/.claude/detector.py              # Detect current zone"
echo "  ~/.claude/detector.py --config     # Show zone config"
echo "  ~/.claude/detector.py /some/path   # Check specific path"
echo ""
echo "Customize zones:"
echo "  Edit $CONFIG_FILE"
echo "  Edit zone behaviors in $ZONES_DIR/"
echo ""
