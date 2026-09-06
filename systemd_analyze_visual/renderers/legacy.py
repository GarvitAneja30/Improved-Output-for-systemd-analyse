"""
Legacy blame format (backward compatible)
"""

from typing import List
from ..models import ProcessedService

class LegacyRenderer:
    """Render in original systemd-analyze blame format"""
    
    @staticmethod
    def render(services: List[ProcessedService]) -> str:
        """Render as blame list"""
        lines = []
        
        # Sort by duration (descending)
        sorted_services = sorted(services, 
                                key=lambda x: x.duration_ms, 
                                reverse=True)
        
        for service in sorted_services:
            time_str = f"{service.duration_ms/1000:.1f}s"
            lines.append(f"{time_str:>10}  {service.name}")
        
        return "\n".join(lines)