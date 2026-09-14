"""
Filtering and sorting logic
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from systemd_analyze_visual.models import ProcessedService, BootMetrics

class FilterCriteria:
    """Filtering criteria"""
    def __init__(self,
                 min_time_s: float = 0,
                 max_time_s: float = 999999,
                 severity: Optional[str] = None,
                 name_pattern: Optional[str] = None,
                 dependency: Optional[str] = None):
        self.min_time_ms = min_time_s * 1000
        self.max_time_ms = max_time_s * 1000
        self.severity = severity
        self.name_pattern = name_pattern
        self.dependency = dependency


def apply_filters(metrics: BootMetrics,
                 filters: FilterCriteria) -> BootMetrics:
    """Apply filtering to services"""
    
    filtered = metrics.services
    
    # Filter by time range
    filtered = [s for s in filtered
               if filters.min_time_ms <= s.duration_ms <= filters.max_time_ms]
    
    # Filter by severity
    if filters.severity:
        severity_levels = {
            'ok': ['OK'],
            'warn': ['WARN'],
            'orange': ['ORANGE'],
            'critical': ['CRITICAL'],
            'slow': ['ORANGE', 'CRITICAL'],
            'problem': ['WARN', 'ORANGE', 'CRITICAL']
        }
        severities = severity_levels.get(filters.severity.lower(), 
                                        [filters.severity])
        filtered = [s for s in filtered if s.severity in severities]
    
    # Filter by name pattern
    if filters.name_pattern:
        import re
        try:
            pattern = re.compile(filters.name_pattern)
            filtered = [s for s in filtered if pattern.search(s.name)]
        except re.error:
            pass  # Invalid regex, skip
    
    # Filter by dependency
    if filters.dependency:
        # Show only services related to this dependency
        dep_related = {filters.dependency}
        
        # Find all services this depends on
        for service in metrics.services:
            if filters.dependency in service.dependencies:
                dep_related.add(service.name)
        
        # Find all services that depend on this
        for service in metrics.services:
            if filters.dependency in service.reverse_deps:
                dep_related.add(service.name)
        
        filtered = [s for s in filtered if s.name in dep_related]
    
    return BootMetrics(
        total_boot_ms=metrics.total_boot_ms,
        kernel_time_ms=metrics.kernel_time_ms,
        userspace_time_ms=metrics.userspace_time_ms,
        services=filtered,
        critical_path=metrics.critical_path
    )


def sort_services(services: List[ProcessedService],
                 sort_key: str = 'duration',
                 reverse: bool = True) -> List[ProcessedService]:
    """Sort services by various criteria"""
    
    sort_functions = {
        'duration': lambda s: s.duration_ms,
        'time': lambda s: s.duration_ms,
        'name': lambda s: s.name,
        'severity': lambda s: {'OK': 0, 'WARN': 1, 'ORANGE': 2, 
                              'CRITICAL': 3}.get(s.severity, 0),
        'depth': lambda s: s.depth,
        'start': lambda s: s.start_time_ms,
    }
    
    key_func = sort_functions.get(sort_key.lower(), 
                                 sort_functions['duration'])
    
    return sorted(services, key=key_func, reverse=reverse)