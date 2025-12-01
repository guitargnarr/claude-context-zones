# Parallel Development Zone Behaviors

## Context
You are working in a git worktree for parallel development. This is one of multiple concurrent Claude instances working on independent tasks. Coordination and isolation are critical.

## Critical Rules

- **Autonomous execution**: Do NOT wait for user verification mid-task. Make reasonable decisions and proceed.
- **Time-boxed work**: You have 30-45 minutes. Ship what you can, document blockers.
- **No cross-contamination**: Only modify files in YOUR worktree. Never touch main branch files.
- **Progress markers**: Output timestamped progress every 10-15 minutes.

## Completion Standards

Before marking task complete:
1. Code compiles/passes linting
2. Tests pass (or new tests written and passing)
3. Changes committed with descriptive message
4. PR created or ready to create

## Error Handling

If you encounter errors:
1. Try 2-3 different approaches (max 5 min per approach)
2. Document what didn't work
3. Implement what you CAN
4. Create PR with "Known Issues" section if needed
5. Do NOT stop execution - keep progress going

## Output Style

- Timestamped progress markers: `[HH:MM] Completed X, starting Y`
- Concise status updates
- Document blockers immediately when encountered
- Final summary with: completed items, known issues, next steps

## Git Behavior

- Commit early, commit often (functional increments)
- Branch naming: feature/* or fix/* (should already be set by worktree)
- Push before session ends
- Create PR with clear description of changes

## Coordination

- Do NOT modify files outside your assigned scope
- If you need something from another worktree's scope, document it as a dependency
- Your PR will be reviewed and merged by the orchestrator

## 70-85% Completion Acceptable

If you can't complete 100%:
- Deliver working partial implementation
- Document what's missing in PR description
- This is better than blocking on perfection
