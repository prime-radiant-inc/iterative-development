# TaskTracker Spec

## Overview

TaskTracker is a command-line task management tool. Users can create, list, complete, and delete tasks.

## Architecture

Tasks are stored as JSON in a local file (`~/.tasktracker/tasks.json`). The CLI provides subcommands for each operation.

## Out of Scope

- Cloud sync
- Multi-user support
- GUI
