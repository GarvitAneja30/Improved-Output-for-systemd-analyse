# systemd-analyze-visual

Enhanced boot time visualization for systemd.

## Problem

The default `systemd-analyze` output is:
- Hard to scan through textual lists
- Difficult to identify critical path services
- No built-in filtering for slow services

## Solution

`systemd-analyze-visual` provides four complementary views:

| Feature | What It Does |
|---------|-------------|
| **Table View** | Sorted service list with boot times, dependencies |
| **Tree View** | Hierarchical dependency graph of services |
| **Min-time Filter** | Show only services exceeding time threshold |
| **Summary View** | Overall boot time breakdown & metrics |

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Tabular breakdown of all services
systemd-analyze-visual --table

# Dependency tree showing which services block which
systemd-analyze-visual --tree

# Find slow bottlenecks (services taking >1 second)
systemd-analyze-visual --min-time 1.0

# High-level boot metrics summary
systemd-analyze-visual --summary
```

## Requirements

- Python 3.8+
- systemd (Linux only)
- dbus-python

## Coming Soon: strace Integration

Syscall-level analysis for filesystem I/O performance.