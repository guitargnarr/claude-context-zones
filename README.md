# Claude Zones

Context-aware behavior switching for Claude Code based on filesystem location.

## The Problem

Claude Code behaves the same whether you're working on:
- A job application (high stakes, needs tracking)
- Financial data (security critical, needs protection)
- A side project (ship fast, minimal docs)
- Research (exploration allowed, documentation valuable)

One-size-fits-all instructions lead to either over-cautious behavior everywhere or risky behavior where it shouldn't be.

## The Solution

Claude Zones detects your current working directory and loads context-appropriate behavioral instructions automatically.

```
~/Projects/my-startup/     → development zone (ship fast)
~/Documents/Finance/       → finance zone (protect data)
~/Desktop/Job-Search/      → career zone (track everything)
~/Documents/Research/      → research zone (explore freely)
```

## Installation

```bash
git clone https://github.com/yourusername/claude-zones.git
cd claude-zones
chmod +x install.sh
./install.sh
```

## Usage

### Check Current Zone

```bash
~/.claude/detector.py
# Zone: development
# Config: zones/development.md
# Matched: ~/Projects

~/.claude/detector.py --zone-only
# development

~/.claude/detector.py --config
# (outputs the zone's behavioral instructions)
```

### Check Any Path

```bash
~/.claude/detector.py ~/Documents/Finance/taxes
# Zone: finance
# Config: zones/finance.md
```

## Configuration

### Zone Paths

Edit `~/.claude/zones.json` to customize which directories map to which zones:

```json
{
  "career": {
    "paths": [
      "~/Desktop/Job-Search",
      "~/Projects/*resume*"
    ],
    "config": "zones/career.md"
  },
  "finance": {
    "paths": ["~/Documents/Finance"],
    "config": "zones/finance.md"
  }
}
```

Patterns support `*` wildcards. More specific patterns should be listed first.

### Zone Behaviors

Edit the markdown files in `~/.claude/zones/` to customize behaviors:

- `career.md` - Job search, applications, professional communication
- `finance.md` - Financial data, security-first, protect sensitive info
- `development.md` - Standard coding, ship fast, minimal docs
- `research.md` - Exploration, documentation allowed, cite sources
- `default.md` - Fallback for unmatched paths

## Example Zone: Career

```markdown
# Career Zone Behaviors

## Critical Rules
- Track all applications
- Professional tone always
- Never fabricate experience
- Protect salary/negotiation data

## Protected Files
- `**/JOB_TRACKER*.csv`
- `**/salary*.md`
```

## Integration with Claude Code

The detector outputs zone configs that can be referenced in your CLAUDE.md:

```markdown
# In ~/.claude/CLAUDE.md

# Zone-specific behaviors loaded based on pwd
# Run: ~/.claude/detector.py --zone-only
```

## How It Works

1. `detector.py` checks current working directory against configured paths
2. Returns the matching zone name and config file path
3. Zone configs contain behavioral instructions for Claude Code
4. More specific path patterns take precedence

## Included Zones

| Zone | Purpose | Key Behaviors |
|------|---------|---------------|
| `career` | Job search | Track everything, professional tone, protect private data |
| `finance` | Financial work | Security-first, double-check math, audit trail |
| `development` | Coding | Ship fast, test before claiming success, minimal changes |
| `research` | Analysis | Cite sources, document methodology, preserve raw data |
| `default` | Fallback | Standard helpful assistant behavior |

## Creating Custom Zones

1. Add zone definition to `~/.claude/zones.json`
2. Create `~/.claude/zones/your-zone.md` with behavioral instructions
3. Test: `~/.claude/detector.py /path/to/zone/directory`

## Academic Background

Zone-based behavioral switching is grounded in context-aware computing research:

- Craig et al. (2020) - Context-aware digital behavior change interventions
- Hussein et al. (2011) - Model-based development of context-aware adaptive systems

The core insight: systems that adapt behavior based on context outperform one-size-fits-all approaches.

## License

MIT
