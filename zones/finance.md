# Finance Zone Behaviors

## Context
You are working with financial data. Accuracy and security are paramount.

## Critical Rules

- **Never expose sensitive data**: Account numbers, balances, SSN must never appear in logs, commits, or outputs
- **Double-check calculations**: Financial math errors have real consequences
- **Preserve originals**: Always backup before modifying financial files
- **Audit trail**: Log all modifications to financial documents

## Protected Files

Do not read or modify without explicit permission:
- `**/*.csv` (financial CSVs often contain sensitive data)
- `**/accounts*.md`
- `**/budget*.xlsx`
- `**/*tax*`

## Preferred Actions

1. When processing financial data: Validate inputs, show intermediate calculations
2. When generating reports: Include data sources and methodology
3. When modifying spreadsheets: Create backup first, document changes
4. When analyzing spending: Categorize consistently, flag anomalies

## Output Style

- Show your math
- Confirm before any write operations
- Use precise currency formatting
- Round appropriately (2 decimal places for USD)

## Security

- Assume all financial files may contain PII
- Never commit financial data to git
- Warn if sensitive patterns detected in output
