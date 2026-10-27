"""
Legacy blame format (backward compatible)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from systemd_analyze_visual.models import ProcessedService
from systemd_analyze_visual.utils import format_duration

class LegacyRenderer:
    """Render in original systemd-analyze blame format"""
    
    @staticmethod
    def render(services: List[ProcessedService]) -> str:
        """Render as blame list"""
        lines = []
        
        # Like real blame: skip zero-time units, sort slowest first
        sorted_services = sorted((x for x in services if x.duration_ms > 0),
                                key=lambda x: x.duration_ms,
                                reverse=True)
        
        times = [format_duration(x.duration_ms) for x in sorted_services]
        width = max((len(t) for t in times), default=0)
        
        for time_str, service in zip(times, sorted_services):
            lines.append(f"{time_str:>{width}} {service.name}")
        
        return "\n".join(lines)