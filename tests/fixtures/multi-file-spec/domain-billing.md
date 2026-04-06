# Billing Integration

## Usage Tracking

When a task is created, increment the monthly task counter in `~/.tasktracker/usage.json`.

The counter resets on the first of each month.

## Quota Enforcement

If the user has created more than 100 tasks in the current month, `task add` should print `error: monthly quota exceeded (100 tasks)` to stderr and exit 1.

No task is created when the quota is exceeded.
