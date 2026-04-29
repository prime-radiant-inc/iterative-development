# iterative-development for OpenCode

Complete guide for using iterative-development with [OpenCode.ai](https://opencode.ai).

## Installation

Add iterative-development and superpowers to the `plugin` array in your `opencode.json` global or project config:

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git"
  ]
}
```

Restart OpenCode. The iterative-development plugin registers its bundled skills automatically.

## Usage

Use OpenCode's native `skill` tool to list and load skills:

```
use skill tool to list skills
use skill tool to load iterative-development/iterative-development
```

The top-level skill orchestrates the iterative workflow. The supporting skills are also available for direct use:

- `iterative-development/extracting-requirements`
- `iterative-development/scoping-the-simplest-core`
- `iterative-development/running-an-iteration`
- `iterative-development/implementing-tasks`
- `iterative-development/auditing-progress`

## Relationship to superpowers

Install `superpowers` alongside this plugin. `superpowers` provides the general-purpose operating rules, TDD, verification, and OpenCode tool mapping bootstrap. This plugin provides the domain workflow for large-spec iterative development.

## How It Works

The OpenCode plugin does one thing: it registers this package's `skills/` directory through OpenCode's `config` hook. OpenCode then discovers each `SKILL.md` file through its native skill system.

The plugin intentionally does not inject a conversation bootstrap. Bootstrap behavior belongs to `superpowers`; iterative-development should only add its skill pack.

## Updating

OpenCode reinstalls git plugins when it refreshes plugin dependencies. Restart OpenCode after changing plugin config.

To pin a specific version, use a branch or tag:

```json
{
  "plugin": ["iterative-development@git+https://github.com/prime-radiant-inc/iterative-development.git#v0.1.0"]
}
```

## Troubleshooting

### Plugin not loading

1. Check OpenCode logs: `opencode run --print-logs "hello" 2>&1 | grep -i iterative`
2. Verify the plugin line in your `opencode.json`
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use OpenCode's `skill` tool to list available skills
2. Check that the plugin is loading
3. Each skill needs a `SKILL.md` file with valid YAML frontmatter

## Development Checks

Run repository validation, including OpenCode structural checks:

```bash
./scripts/run_validation_suite.sh
```

Run only OpenCode structural checks:

```bash
bash tests/opencode/run-tests.sh
```
