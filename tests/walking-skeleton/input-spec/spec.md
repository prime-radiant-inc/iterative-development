# Greet CLI Spec

## Overview

A tiny command-line tool that greets the user by name. This spec is intentionally minimal — it exists as a dogfood target for the iterative-development plugin walking skeleton.

## Functional requirements

### F-1: Personalized greeting
When the user runs `greet <name>`, the tool prints `Hello, <name>!` to stdout and exits with status 0.

### F-2: Missing argument handling
When the user runs `greet` with no argument, the tool prints `usage: greet <name>` to stderr and exits with a non-zero status.

## Out of scope
- Internationalization
- Configuration files
- Arguments other than the name
- Any feature not mentioned above
