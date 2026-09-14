"""
Data processing and aggregation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Set
from systemd_analyze_visual.models import ServiceTiming, ProcessedService, BootMetrics
from systemd_analyze_visual.critical_path import get_critical_chain, identify_critical_path_services, mark_parallel_services

def process_timings(raw_timings: List[ServiceTiming]) -> BootMetrics:
    """Process raw timings into meaningful data"""
    
    if not raw_timings:
        return BootMetrics(0, 0, 0, [], [])
    
    # Get critical chain data
    chain_output = get_critical_chain()
    critical_services = identify_critical_path_services(chain_output)
    critical_services = mark_parallel_services(critical_services, raw_timings)
    
    # Calculate total boot time from first service
    total_ms = max(s.start_time_ms + s.duration_ms 
                   for s in raw_timings if s.start_time_ms > 0)
    
    # Process each service
    processed = []
    for timing in raw_timings:
        # Check if service is on critical path
        critical_info = critical_services.get(timing.name, {})
        is_critical = critical_info.get('on_critical_path', False)
        blocks_boot = critical_info.get('blocks_boot', False)
        
        # Recalculate severity based on whether it blocks boot
        if not blocks_boot:
            # Non-blocking services get lower severity
            severity = "OK"
        else:
            # Critical path services: use duration
            if timing.duration_ms < 100:
                severity = "OK"
            elif timing.duration_ms < 1000:
                severity = "WARN"
            elif timing.duration_ms < 5000:
                severity = "ORANGE"
            else:
                severity = "CRITICAL"
        
        # Calculate blocking (how many services depend on this)
        block_count = calculate_block_count(timing, raw_timings)
        
        # Calculate parallel count
        parallel_count = calculate_parallel_count(timing, raw_timings)
        
        # Calculate depth
        depth = calculate_depth(timing, raw_timings)
        
        proc_service = ProcessedService(
            name=timing.name,
            duration_ms=timing.duration_ms,
            start_time_ms=timing.start_time_ms,
            severity=severity,
            block_count=block_count,
            parallel_count=parallel_count,
            depth=depth,
            dependencies=timing.dependencies,
            reverse_deps=timing.wanted_by
        )
        processed.append(proc_service)
    
    # Find critical path
    critical_path = list(critical_services.keys())
    
    # Estimate kernel time
    kernel_ms = min((s.start_time_ms for s in raw_timings 
                    if s.start_time_ms > 0), default=0)
    
    metrics = BootMetrics(
        total_boot_ms=int(total_ms),
        kernel_time_ms=int(kernel_ms),
        userspace_time_ms=int(total_ms - kernel_ms),
        services=sorted(processed, key=lambda x: x.duration_ms, 
                       reverse=True),
        critical_path=critical_path
    )
    
    return metrics
    """Process raw timings into meaningful data"""
    
    # Calculate total boot time
    if not raw_timings:
        return BootMetrics(0, 0, 0, [], [])

    # SANITY CHECK: Remove unrealistic timings
    max_realistic_time = 300000  # 5 minutes max
    raw_timings = [s for s in raw_timings 
                  if s.duration_ms < max_realistic_time]
    
    if not raw_timings:
        print("Warning: No realistic timing data found", file=sys.stderr)
        return BootMetrics(0, 0, 0, [], [])

    
    total_ms = max(s.start_time_ms + s.duration_ms 
                   for s in raw_timings if s.start_time_ms > 0)
    
    # Process each service
    processed = []
    for timing in raw_timings:
        # Calculate blocking (how many services this blocks)
        block_count = calculate_block_count(timing, raw_timings)
        
        # Calculate parallel count (concurrent services)
        parallel_count = calculate_parallel_count(timing, raw_timings)
        
        # Calculate depth in dependency tree
        depth = calculate_depth(timing, raw_timings)
        
        proc_service = ProcessedService(
            name=timing.name,
            duration_ms=timing.duration_ms,
            start_time_ms=timing.start_time_ms,
            severity=timing.severity,
            block_count=block_count,
            parallel_count=parallel_count,
            depth=depth,
            dependencies=timing.dependencies,
            reverse_deps=timing.wanted_by
        )
        processed.append(proc_service)
    
    # Find critical path
    critical_path = find_critical_path(raw_timings)
    
    # Estimate kernel time (first service start - some offset)
    kernel_ms = min((s.start_time_ms for s in raw_timings 
                    if s.start_time_ms > 0), default=0)
    
    metrics = BootMetrics(
        total_boot_ms=int(total_ms),
        kernel_time_ms=int(kernel_ms),
        userspace_time_ms=int(total_ms - kernel_ms),
        services=sorted(processed, key=lambda x: x.duration_ms, 
                       reverse=True),
        critical_path=critical_path
    )
    
    return metrics


def calculate_block_count(service: ServiceTiming, 
                         all_services: List[ServiceTiming]) -> int:
    """Count services blocked by this one"""
    # A service blocks others that depend on it
    return len(service.wanted_by)


def calculate_parallel_count(service: ServiceTiming,
                            all_services: List[ServiceTiming]) -> int:
    """Count services running concurrently"""
    count = 0
    service_end = service.start_time_ms + service.duration_ms
    
    for other in all_services:
        if other.name == service.name:
            continue
        
        # Check if other service runs during this service
        other_end = other.start_time_ms + other.duration_ms
        if (service.start_time_ms <= other.start_time_ms < service_end or
            service.start_time_ms < other_end <= service_end):
            count += 1
    
    return count


def calculate_depth(service: ServiceTiming,
                   all_services: List[ServiceTiming]) -> int:
    """Calculate dependency graph depth"""
    if not service.dependencies:
        return 1
    
    # Simple BFS approach
    max_depth = 0
    visited = set()
    queue = [(service, 0)]
    
    while queue:
        current, depth = queue.pop(0)
        
        if current.name in visited:
            continue
        visited.add(current.name)
        max_depth = max(max_depth, depth)
        
        for dep_name in current.dependencies:
            dep = next((s for s in all_services 
                       if s.name == dep_name), None)
            if dep and dep.name not in visited:
                queue.append((dep, depth + 1))
    
    return max_depth


def find_critical_path(services: List[ServiceTiming]) -> List[str]:
    """Find services on the critical boot path"""
    if not services:
        return []
    
    critical = []
    max_time = 0
    
    for service in services:
        path_time = calculate_path_time(service, services, set())  # Pass empty set
        if path_time > max_time:
            max_time = path_time
            critical = [service.name]
    
    return critical

def calculate_path_time(service: ServiceTiming,
                       all_services: List[ServiceTiming],
                       visited: Set = None) -> int:
    """Calculate total time for dependency chain"""
    if visited is None:
        visited = set()
    
    if service.name in visited:
        return 0  # Already counted, avoid infinite recursion
    
    visited.add(service.name)
    total = service.duration_ms
    
    for dep_name in service.dependencies:
        dep = next((s for s in all_services 
                   if s.name == dep_name), None)
        if dep and dep.name not in visited:
            total += calculate_path_time(dep, all_services, visited)
    
    return total