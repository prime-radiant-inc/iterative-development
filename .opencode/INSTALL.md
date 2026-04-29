# Installing iterative-development for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- The [superpowers](https://github.com/obra/superpowers) OpenCode plugin installed for the intended workflow

## Installation

Add both plugins to the `plugin` array in your `opencode.json` global or project config:

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git"
  ]
}
```

Restart OpenCode. The plugin registers all iterative-development skills automatically.

Verify by using OpenCode's native `skill` tool to list skills, then load `iterative-development/iterative-development`.

## Usage

Use OpenCode's native `skill` tool:

```
use skill tool to list skills
use skill tool to load iterative-development/iterative-development
```

## Updating

OpenCode reinstalls git plugins when it refreshes plugin dependencies. Restart OpenCode after changing plugin config.

To pin a specific version:

```json
{
  "plugin": ["iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git#<tag-or-commit>"]
}
```

Replace `<tag-or-commit>` with a real tag, branch, or commit SHA.

## Troubleshooting

### Plugin not loading

1. Check logs: `opencode run --print-logs "hello" 2>&1 | grep -i iterative`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use OpenCode's `skill` tool to list discovered skills
2. Check that the plugin is loading
3. Verify the package has `.opencode/plugins/iterative-development.js` and `skills/*/SKILL.md`

## Getting Help

- Report issues: https://github.com/prime-radiant-inc/iterative-development/issues
- Full documentation: ../docs/README.opencode.md
