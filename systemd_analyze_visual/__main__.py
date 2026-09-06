"""
Entry point for python -m systemd_analyze_visual
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())