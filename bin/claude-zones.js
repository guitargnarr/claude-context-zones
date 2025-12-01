#!/usr/bin/env node

/**
 * Claude Context Zones - Context-aware behavior switching for Claude Code
 *
 * Detects your working directory and loads context-appropriate behavioral
 * instructions automatically.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Default zone definitions
const DEFAULT_ZONES = {
  career: {
    paths: [
      '~/Desktop/1_PRIORITY_JOB_SEARCH',
      '~/Documents/Career',
      '~/Projects/*job*',
      '~/Projects/*resume*',
    ],
    config: 'zones/career.md'
  },
  finance: {
    paths: [
      '~/Documents/Finance',
      '~/Projects/*budget*',
      '~/Projects/*tax*',
    ],
    config: 'zones/finance.md'
  },
  development: {
    paths: [
      '~/Projects',
      '~/Code',
      '~/Developer',
    ],
    config: 'zones/development.md'
  },
  research: {
    paths: [
      '~/Documents/Research',
      '~/Projects/*research*',
      '~/Projects/*analysis*',
    ],
    config: 'zones/research.md'
  }
};

/**
 * Expand ~ to home directory
 */
function expandPath(p) {
  if (p.startsWith('~/')) {
    return path.join(os.homedir(), p.slice(2));
  }
  return p;
}

/**
 * Check if current path matches a zone pattern (supports * wildcards)
 */
function pathMatches(current, pattern) {
  const expandedPattern = expandPath(pattern);

  // Handle wildcards
  if (expandedPattern.includes('*')) {
    const patternParts = expandedPattern.split(path.sep);
    const currentParts = current.split(path.sep);

    if (currentParts.length < patternParts.length) {
      return false;
    }

    for (let i = 0; i < patternParts.length; i++) {
      const patternPart = patternParts[i];
      const currentPart = currentParts[i];

      if (!currentPart) return false;

      // Simple wildcard matching
      if (patternPart.includes('*')) {
        const regex = new RegExp('^' + patternPart.replace(/\*/g, '.*') + '$', 'i');
        if (!regex.test(currentPart)) {
          return false;
        }
      } else if (patternPart.toLowerCase() !== currentPart.toLowerCase()) {
        return false;
      }
    }
    return true;
  } else {
    // Check if current is under pattern directory
    const resolved = path.resolve(expandedPattern);
    const currentResolved = path.resolve(current);
    return currentResolved.startsWith(resolved);
  }
}

/**
 * Detect which zone the given path belongs to
 */
function detectZone(checkPath, zones) {
  checkPath = checkPath || process.cwd();
  zones = zones || loadUserZones() || DEFAULT_ZONES;

  const current = path.resolve(checkPath);

  for (const [zoneName, zoneConfig] of Object.entries(zones)) {
    for (const pattern of zoneConfig.paths) {
      if (pathMatches(current, pattern)) {
        return {
          zone: zoneName,
          config: zoneConfig.config,
          matched_pattern: pattern,
          path: current
        };
      }
    }
  }

  return {
    zone: 'default',
    config: 'zones/default.md',
    matched_pattern: null,
    path: current
  };
}

/**
 * Load user's custom zone configuration
 */
function loadUserZones() {
  const configPath = path.join(os.homedir(), '.claude', 'zones.json');
  try {
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    }
  } catch (e) {
    // Fall back to defaults
  }
  return null;
}

/**
 * Load the zone configuration file content
 */
function loadZoneConfig(configPath) {
  // Look in user's .claude directory first
  const userPath = path.join(os.homedir(), '.claude', configPath);
  if (fs.existsSync(userPath)) {
    return fs.readFileSync(userPath, 'utf8');
  }

  // Look relative to this script (for bundled configs)
  const scriptDir = path.dirname(__dirname);
  const bundledPath = path.join(scriptDir, configPath);
  if (fs.existsSync(bundledPath)) {
    return fs.readFileSync(bundledPath, 'utf8');
  }

  return `# Zone config not found: ${configPath}`;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    path: null,
    json: false,
    config: false,
    zoneOnly: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--json') {
      options.json = true;
    } else if (arg === '--config') {
      options.config = true;
    } else if (arg === '--zone-only') {
      options.zoneOnly = true;
    } else if (arg === '--help' || arg === '-h') {
      options.help = true;
    } else if (!arg.startsWith('-')) {
      options.path = arg;
    }
  }

  return options;
}

/**
 * Print help message
 */
function printHelp() {
  console.log(`
claude-zones - Context-aware behavior switching for Claude Code

Usage: claude-zones [options] [path]

Options:
  --json        Output as JSON
  --config      Output the zone's configuration content
  --zone-only   Output only the zone name
  -h, --help    Show this help message

Examples:
  claude-zones                    # Detect zone for current directory
  claude-zones ~/Projects/myapp   # Detect zone for specific path
  claude-zones --zone-only        # Output just the zone name
  claude-zones --config           # Output zone configuration

Configuration:
  Edit ~/.claude/zones.json to customize zone mappings
  Edit ~/.claude/zones/*.md to customize zone behaviors
`);
}

/**
 * Main entry point
 */
function main() {
  const options = parseArgs();

  if (options.help) {
    printHelp();
    process.exit(0);
  }

  const result = detectZone(options.path);

  if (options.zoneOnly) {
    console.log(result.zone);
  } else if (options.config) {
    console.log(loadZoneConfig(result.config));
  } else if (options.json) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`Zone: ${result.zone}`);
    console.log(`Config: ${result.config}`);
    if (result.matched_pattern) {
      console.log(`Matched: ${result.matched_pattern}`);
    }
  }
}

main();
