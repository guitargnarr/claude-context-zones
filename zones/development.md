# Development Zone Behaviors

## Context
Standard software development context. Code quality and shipping matter.

## Critical Rules

- **Working code > documentation**: Prove it works before documenting
- **Test before claiming success**: Run the tests, show the output
- **Minimal changes**: Don't refactor code you weren't asked to touch
- **Security awareness**: Never commit secrets, credentials, or API keys

## Preferred Actions

1. When writing code: Follow existing patterns in the codebase
2. When fixing bugs: Understand root cause before patching
3. When adding features: Keep scope minimal, ship incrementally
4. When reviewing: Focus on correctness, then style

## Output Style

- Concise explanations
- Show command outputs when relevant
- Code examples over lengthy descriptions

## Git Behavior

- Commit messages: Imperative mood, explain "why" not "what"
- Never force push to main/master
- Run tests before suggesting commit

## Build & Deploy

- Verify build passes locally before deploying
- Check for TypeScript/lint errors
- Test the deployed version, not just local
