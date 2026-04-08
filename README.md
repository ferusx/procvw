# procvw

procvw is a lightweight BSD process viewer designed in the spirit of
traditional UNIX tools.

It provides a clear and structured view of running processes through
multiple output modes, including a clean tabular layout, a hierarchical
tree view, and JSON export for further processing.

## Features

- Clean tabular process view (default)
- Tree view with parent/child relationships
- JSON export and load support
- CPU-aware sorting and filtering
- Configurable output (colors, wrapping, depth)
- Accurate process state (STAT column)
- Support for both short and full command display

## Usage

```bash
# Basic process view
procvw

# Tree view
procvw --tree

# Sort by CPU
procvw -s cpu

# Sort by process state
procvw -s stat

# Limit output
procvw -n 10

# Show full command paths
procvw --show-path

# Tree with depth limit
procvw --tree --tree-depth 2

# Show subtree CPU
procvw --tree --cpu-all

# Export to JSON
procvw --tree --json > processes.json

# Load from JSON
procvw --load processes.json --table
```

## Options

### Common options

- `--tree`  
  Display processes in hierarchical tree view

- `--table`  
  Display processes in flat table view (used with `--load`)

- `-s, --sort {cpu,mem,pid,rss,cmd,thr,stat}`  
  Sort processes by selected field

- `-b, --bottom`  
  Reverse sort order

- `-n, --number N`  
  Limit number of displayed processes

- `--show-path`  
  Display full command with arguments instead of short name

- `--json`  
  Output process data in JSON format

- `--load FILE`  
  Load process data from a JSON file

- `--save FILE`  
  Save current process data to a JSON file

---

### Tree-specific options

- `--tree-depth N`  
  Limit depth of the process tree

- `--cpu-all`  
  Show subtree CPU usage for all nodes

- `--cpu-threshold VALUE`  
  Show subtree CPU only for nodes above threshold

- `--prune LEVEL`  
  Prune low-value branches (higher = more aggressive)

---

## Design Philosophy

procvw is built with a focus on clarity, correctness, and simplicity.

The goal is not to replicate large, feature-heavy monitoring tools,
but to provide a fast and reliable way to inspect process state with
minimal friction.

Key principles:

- Keep output readable and structured
- Prefer explicit behavior over implicit assumptions
- Avoid hidden magic or silent failures
- Ensure consistent behavior across all output modes
- Make features discoverable through examples, not complexity

procvw follows the traditional UNIX philosophy:
do one thing well, and make it composable.
























