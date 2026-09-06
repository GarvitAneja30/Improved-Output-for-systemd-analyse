# systemd-analyze-visual

Enhanced boot time visualization for systemd.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Table view
systemd-analyze-visual --table

# Tree view
systemd-analyze-visual --tree

# Filter slow services
systemd-analyze-visual --min-time 1.0

# Show summary
systemd-analyze-visual --summary
```

## Requirements

- Python 3.8+
- systemd (Linux only)
- dbus-python