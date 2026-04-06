# User-Facing Commands

## Creating Tasks

When the user runs `task add <title>`, a new task is created with:
- A unique numeric ID (auto-incremented)
- The provided title
- Status: "pending"
- Creation timestamp

The tool prints `Created task #<id>: <title>` to stdout and exits 0.

If no title is provided, print `usage: task add <title>` to stderr and exit 1.

## Listing Tasks

When the user runs `task list`, all tasks are displayed in a table:
```
ID  Status   Title
1   pending  Buy groceries
2   done     Write tests
```

If no tasks exist, print `No tasks.` and exit 0.

## Completing Tasks

When the user runs `task done <id>`, the task with that ID is marked as "done".

Print `Completed task #<id>: <title>` to stdout and exit 0.

If the ID doesn't exist, print `error: task #<id> not found` to stderr and exit 1.
