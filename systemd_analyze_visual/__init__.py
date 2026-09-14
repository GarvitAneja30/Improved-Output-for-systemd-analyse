"""
systemd-analyze-visual
Enhanced boot time visualization for systemd
"""

__version__ = '0.1.0'
__author__ = 'Your Name'

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systemd_analyze_visual.models import ServiceTiming, BootMetrics
from systemd_analyze_visual.collector import collect_timings
from systemd_analyze_visual.processor import process_timings

__all__ = [
    'ServiceTiming',
    'BootMetrics',
    'collect_timings',
    'process_timings',
]