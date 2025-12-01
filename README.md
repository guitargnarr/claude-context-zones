# claude-context-zones

[![PyPI version](https://badge.fury.io/py/claude-context-zones.svg)](https://pypi.org/project/claude-context-zones/)
[![npm version](https://badge.fury.io/js/claude-context-zones.svg)](https://www.npmjs.com/package/claude-context-zones)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Context-aware behavior switching for Claude Code based on filesystem location.**

Make your AI assistant adapt its behavior based on where you're working - stricter in finance directories, more exploratory in research folders, security-conscious everywhere it matters.

## What's New in v1.1.0

- **Hook Integration** - Automatic zone loading at session start
- **MCP Server** - Dynamic zone switching mid-session
- **Zone Inheritance** - Compose behaviors from multiple zones
- **Project Overrides** - `.claude-zone` file for per-project control
- **Usage Metrics** - Track which zones you use most
- **Parallel Development** - Built-in zone for worktree-based parallel work

## Why This Exists

Claude Code uses a single `CLAUDE.md` file for behavioral instructions. But your work contexts are different:

| Context | What You Need |
|---------|---------------|
| Job applications | Track everything, professional tone, protect salary info |
| Financial data | Security-first, double-check math, never expose account numbers |
| Side projects | Ship fast, minimal docs, trust the developer |
| Research | Explore freely, cite sources, preserve raw data |
| Parallel dev | Autonomous execution, time-boxed, no cross-contamination |

**One-size-fits-all instructions create friction.** You either get over-cautious behavior everywhere or risky behavior where it shouldn't be.

## The Solution

Claude Context Zones detects your working directory and loads context-appropriate instructions:

```
~/Projects/startup/           → development (ship fast)
~/Documents/Finance/          → finance (protect data)
~/Desktop/Job-Search/         → career (track everything)
~/Documents/Research/         → research (explore freely)
~/Projects/.worktrees/feat-x/ → parallel (autonomous execution)
```

## Installation

### Via pip (recommended)

```bash
pip install claude-context-zones
```

### Via npm

```bash
npm install -g claude-context-zones
```

### From source

```bash
git clone https://github.com/guitargnarr/claude-context-zones.git
cd claude-context-zones
pip install -e .
```

## Quick Start

### 1. Initialize configuration

```bash
claude-zones --init
# Creates ~/.claude/zones.json and example hook
```

### 2. Detect your current zone

```bash
claude-zones
# Zone: development
# Config: zones/development.md
# Matched: ~/Projects
```

### 3. See zone-specific instructions

```bash
claude-zones --config
# Outputs the behavioral instructions for your current zone
```

### 4. Set up automatic loading (recommended)

```bash
# Generate and install the hook script
claude-zones --hook > ~/.claude/hooks/session-start.sh
chmod +x ~/.claude/hooks/session-start.sh
```

Now zone instructions load automatically when you start Claude Code!

## CLI Reference

```bash
# Basic usage
claude-zones [path]              # Detect zone (default: current directory)
claude-zones --zone-only         # Output only zone name
claude-zones --config            # Output zone's behavioral instructions
claude-zones --with-inheritance  # Include inherited zone configs
claude-zones --json              # Output as JSON

# Setup & management
claude-zones --init              # Initialize user config in ~/.claude/
claude-zones --hook              # Output hook script for auto-loading
claude-zones --list-zones        # List all available zones

# Metrics
claude-zones --log               # Log this detection for metrics
claude-zones --metrics           # Show usage statistics

# Help
claude-zones --help              # Show all options
```

## New Features

### Hook Integration (Automatic Zone Loading)

Instead of manually checking zones, have them load automatically:

```bash
# Generate hook script
claude-zones --hook > ~/.claude/hooks/session-start.sh
chmod +x ~/.claude/hooks/session-start.sh
```

Now every Claude Code session starts with the appropriate zone context.

### MCP Server (Dynamic Zone Switching)

Switch zones mid-session without restarting Claude Code.

**Setup:**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "claude-zones": {
      "command": "claude-zones-mcp"
    }
  }
}
```

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `detect_zone` | Get current zone based on working directory |
| `get_zone_config` | Get behavioral instructions for a zone |
| `switch_zone` | Manually switch to a different zone |
| `list_zones` | List all available zones |
| `get_metrics` | Get zone usage statistics |
| `clear_override` | Return to auto-detection |

**Usage in Claude:**
```
"Switch to finance mode" → Claude calls switch_zone tool
"What zone am I in?" → Claude calls detect_zone tool
```

### Zone Inheritance

Create zones that inherit behaviors from other zones:

```json
{
  "client-finance": {
    "paths": ["~/Projects/clients/bank-corp/*"],
    "inherits": ["development", "finance"],
    "config": "zones/client-finance.md"
  }
}
```

This zone gets:
1. Its own specific rules (client-finance.md)
2. Development zone behaviors
3. Finance zone security rules

View inheritance chain:
```bash
claude-zones --config --with-inheritance
```

### Project-Level Overrides

Create a `.claude-zone` file in any project to override auto-detection:

```bash
# ~/Projects/my-startup/.claude-zone
development
# This project is always development mode, regardless of path
```

The file is simple: first non-comment line is the zone name.

### Usage Metrics

Track which zones you use most:

```bash
claude-zones --metrics
# Total detections: 247
#
# Zone usage counts:
#   development: 189
#   career: 32
#   research: 18
#   finance: 8
#
# Recent:
#   development - /Users/me/Projects/startup
#   career - /Users/me/Desktop/Job-Search
```

Enable logging for all detections:
```bash
claude-zones --log  # Logs to ~/.claude/zone-history.log
```

### Parallel Development Zone

Built-in zone for git worktree-based parallel development:

```json
{
  "parallel": {
    "paths": ["~/Projects/.worktrees/*", "*/.worktrees/*"],
    "inherits": ["development"],
    "config": "zones/parallel.md"
  }
}
```

Key behaviors:
- Autonomous execution (no waiting for verification)
- Time-boxed work (30-45 min)
- Progress markers every 10-15 min
- 70-85% completion acceptable
- Error handling with documented blockers

## Configuration

### Zone Definitions

Edit `~/.claude/zones.json` to map directories to zones:

```json
{
  "career": {
    "paths": [
      "~/Desktop/Job-Search",
      "~/Projects/*resume*",
      "~/Projects/*job*"
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
      "~/Projects/*analysis*"
    ],
    "config": "zones/research.md"
  },
  "client-vip": {
    "paths": ["~/Projects/clients/vip-corp/*"],
    "inherits": ["development"],
    "config": "zones/client-vip.md"
  }
}
```

**Pattern matching:**
- `~` expands to home directory
- `*` matches any characters (e.g., `*resume*` matches `my-resume-v2`)
- More specific patterns listed first take precedence

### Zone Behaviors

Edit markdown files in `~/.claude/zones/` to customize instructions:

```
~/.claude/zones/
├── career.md       # Job search context
├── finance.md      # Financial data context
├── development.md  # Coding context
├── research.md     # Analysis context
├── parallel.md     # Parallel development
└── default.md      # Fallback
```

## Built-in Zones

### Career Zone (`career.md`)

For job search, applications, professional communication.

**Key behaviors:**
- Track all applications, contacts, follow-ups
- Professional tone in all generated content
- Never fabricate experience or skills
- Protect salary expectations and negotiation data

**Protected files:** `JOB_TRACKER*.csv`, `salary*.md`, `offers*.md`

### Finance Zone (`finance.md`)

For financial data, budgets, sensitive information.

**Key behaviors:**
- Never expose account numbers, balances, SSN
- Double-check all calculations
- Create backups before modifying files
- Maintain audit trail

**Protected files:** All CSVs, `accounts*.md`, `budget*.xlsx`

### Development Zone (`development.md`)

For coding, side projects, software development.

**Key behaviors:**
- Working code before documentation
- Test before claiming success
- Minimal changes (don't refactor untouched code)
- Never commit secrets or API keys

### Research Zone (`research.md`)

For analysis, exploration, learning.

**Key behaviors:**
- Cite sources, don't fabricate citations
- Distinguish fact from inference
- Preserve raw data, work on copies
- Document methodology

### Parallel Zone (`parallel.md`)

For git worktree-based parallel development.

**Key behaviors:**
- Autonomous execution without user verification
- Time-boxed work (30-45 min)
- Progress markers every 10-15 min
- 70-85% completion acceptable
- Document blockers, don't block on perfection

### Default Zone (`default.md`)

Fallback for unmatched paths.

**Key behaviors:**
- Standard helpful assistant
- Confirm before destructive commands
- Admit uncertainty

## Creating Custom Zones

### 1. Add zone definition

Edit `~/.claude/zones.json`:

```json
{
  "client-acme": {
    "paths": ["~/Projects/clients/acme/*"],
    "inherits": ["development"],
    "config": "zones/client-acme.md"
  }
}
```

### 2. Create zone config

Create `~/.claude/zones/client-acme.md`:

```markdown
# Client: ACME Corp

## Context
Working on ACME Corp projects. Billable work, client-facing.

## Critical Rules
- Follow ACME coding standards (see their wiki)
- All commits must reference ticket numbers
- No external dependencies without approval
- Time tracking required

## Protected Files
- `**/credentials*`
- `**/.env*`
```

### 3. Test

```bash
claude-zones ~/Projects/clients/acme/webapp
# Zone: client-acme
# Inherits: client-acme → development
```

## Integration with Claude Code

### Option 1: Automatic via hooks (recommended)

```bash
claude-zones --hook > ~/.claude/hooks/session-start.sh
chmod +x ~/.claude/hooks/session-start.sh
```

### Option 2: MCP Server (dynamic switching)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "claude-zones": {
      "command": "claude-zones-mcp"
    }
  }
}
```

### Option 3: Manual reference

Add to your `~/.claude/CLAUDE.md`:

```markdown
# Zone-based behaviors
# Run `claude-zones --config` to see current zone instructions
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    claude-zones CLI                          │
├─────────────────────────────────────────────────────────────┤
│  1. Check for .claude-zone override in project              │
│  2. Get current working directory (or provided path)        │
│  3. Load zone definitions from ~/.claude/zones.json         │
│  4. Match path against zone patterns (first match wins)     │
│  5. Resolve inheritance chain                               │
│  6. Return zone name + config + inheritance                 │
│  7. Optionally output merged config content                 │
│  8. Log to metrics if --log flag                            │
└─────────────────────────────────────────────────────────────┘
```

**Matching priority:**
1. `.claude-zone` file in project (highest)
2. Patterns checked in order from zones.json
3. Put more specific patterns first

```json
{
  "client-vip": { "paths": ["~/Projects/clients/vip-corp/*"] },
  "client": { "paths": ["~/Projects/clients/*"] },
  "development": { "paths": ["~/Projects"] }
}
```

## Academic Background

Zone-based behavioral switching is grounded in context-aware computing research:

- **Craig et al. (2020)** - *Systematic review of context-aware digital behavior change interventions to improve health.* Translational Behavioral Medicine. [PMC8158169](https://pmc.ncbi.nlm.nih.gov/articles/PMC8158169/)

- **Hussein et al. (2011)** - *An Approach to Model-Based Development of Context-Aware Adaptive Systems.* IEEE 35th Annual Computer Software and Applications Conference. [IEEE Xplore](https://ieeexplore.ieee.org/document/6032344/)

**Core insight:** Systems that adapt behavior based on context outperform one-size-fits-all approaches. This principle, proven in healthcare and adaptive software, applies equally to AI assistant configuration.

## Troubleshooting

### Zone not detected correctly

1. Check path matching: `claude-zones --json /your/path`
2. Check for `.claude-zone` override: `ls -la .claude-zone`
3. Verify `~/.claude/zones.json` syntax
4. Ensure more specific patterns come first
5. Check inheritance: `claude-zones --config --with-inheritance`

### Config file not found

1. Run `claude-zones --config` to see which file it's looking for
2. Check `~/.claude/zones/` directory exists
3. Verify file permissions
4. Run `claude-zones --init` to create defaults

### Hook not loading

1. Verify hook is executable: `ls -la ~/.claude/hooks/`
2. Check hook syntax: `bash -n ~/.claude/hooks/session-start.sh`
3. Ensure claude-zones is in PATH

### MCP server issues

1. Check server is running: `claude-zones-mcp` in terminal
2. Verify config in `claude_desktop_config.json`
3. Check Claude Code logs for MCP errors

### Changes not taking effect

Zone configs are read fresh each time. If changes aren't appearing:
1. Check you're editing the right file (`~/.claude/zones/`)
2. Verify no syntax errors in your zone markdown
3. Clear any manual override: MCP `clear_override` tool

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Built by [Matthew Scott](https://github.com/guitargnarr) as part of an AI-native development toolkit.

---

**Origin:** This tool emerged from research on context-aware AI configuration in the [from-the-command-before-time](https://github.com/guitargnarr/from-the-command-before-time) analysis project, which identified "zone-based behavioral switching" as a novel, academically-grounded pattern for Claude Code optimization.
