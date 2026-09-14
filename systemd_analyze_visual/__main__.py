"""
Entry point for python -m systemd_analyze_visual
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systemd_analyze_visual.cli import main

if __name__ == '__main__':
    sys.exit(main())