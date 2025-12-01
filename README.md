# claude-context-zones

[![PyPI version](https://badge.fury.io/py/claude-context-zones.svg)](https://pypi.org/project/claude-context-zones/)
[![npm version](https://badge.fury.io/js/claude-context-zones.svg)](https://www.npmjs.com/package/claude-context-zones)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Context-aware behavior switching for Claude Code based on filesystem location.**

Make your AI assistant adapt its behavior based on where you're working - stricter in finance directories, more exploratory in research folders, security-conscious everywhere it matters.

## Why This Exists

Claude Code uses a single `CLAUDE.md` file for behavioral instructions. But your work contexts are different:

| Context | What You Need |
|---------|---------------|
| Job applications | Track everything, professional tone, protect salary info |
| Financial data | Security-first, double-check math, never expose account numbers |
| Side projects | Ship fast, minimal docs, trust the developer |
| Research | Explore freely, cite sources, preserve raw data |

**One-size-fits-all instructions create friction.** You either get over-cautious behavior everywhere or risky behavior where it shouldn't be.

## The Solution

Claude Context Zones detects your working directory and loads context-appropriate instructions:

```
~/Projects/startup/        → development (ship fast)
~/Documents/Finance/       → finance (protect data)
~/Desktop/Job-Search/      → career (track everything)
~/Documents/Research/      → research (explore freely)
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
./install.sh
```

## Quick Start

### 1. Detect your current zone

```bash
claude-zones
# Zone: development
# Config: zones/development.md
# Matched: ~/Projects
```

### 2. See zone-specific instructions

```bash
claude-zones --config
# Outputs the behavioral instructions for your current zone
```

### 3. Check any path

```bash
claude-zones ~/Documents/Finance/taxes-2024
# Zone: finance
# Config: zones/finance.md
```

## CLI Reference

```bash
claude-zones [path]           # Detect zone (default: current directory)
claude-zones --zone-only      # Output only zone name
claude-zones --config         # Output zone's behavioral instructions
claude-zones --json           # Output as JSON
claude-zones --help           # Show help
```

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
```

## Integration with Claude Code

### Option 1: Manual reference

Add to your `~/.claude/CLAUDE.md`:

```markdown
# Zone-based behaviors
# Current zone: $(claude-zones --zone-only)
# Load zone config with: claude-zones --config
```

### Option 2: Dynamic loading (advanced)

Claude Code doesn't natively support dynamic file loading, but you can:

1. Use a shell alias to print zone config before starting:
   ```bash
   alias claude-work='claude-zones --config && claude'
   ```

2. Reference zone configs in project-level `CLAUDE.md` files

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    claude-zones CLI                      │
├─────────────────────────────────────────────────────────┤
│  1. Get current working directory (or provided path)    │
│  2. Load zone definitions from ~/.claude/zones.json     │
│  3. Match path against zone patterns (first match wins) │
│  4. Return zone name + config file path                 │
│  5. Optionally output zone config content               │
└─────────────────────────────────────────────────────────┘
```

**Matching priority:** Patterns are checked in order. Put more specific patterns first:

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
2. Verify `~/.claude/zones.json` syntax
3. Ensure more specific patterns come first

### Config file not found

1. Run `claude-zones --config` to see which file it's looking for
2. Check `~/.claude/zones/` directory exists
3. Verify file permissions

### Changes not taking effect

Zone configs are read fresh each time. If changes aren't appearing:
1. Check you're editing the right file (`~/.claude/zones/`)
2. Verify no syntax errors in your zone markdown

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

**Related:** This tool emerged from research on context-aware AI configuration. See the [analysis](docs/analysis.md) for the full story.
