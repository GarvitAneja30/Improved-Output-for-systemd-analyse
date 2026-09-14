"""
Dependency graph builder
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Dict, Set
from systemd_analyze_visual.models import ServiceTiming, ServiceNode

def build_dependency_graph(services: List[ServiceTiming]) -> Dict[str, ServiceNode]:
    """Build dependency graph from services"""
    
    nodes = {}
    
    # Create nodes for each service
    for service in services:
        node = ServiceNode(
            name=service.name,
            duration_ms=service.duration_ms,
            dependencies=service.dependencies,
            reverse_deps=service.wanted_by,
            depth=0
        )
        nodes[service.name] = node
    
    # Calculate depth using BFS
    for service_name in nodes:
        nodes[service_name].depth = calculate_depth(service_name, nodes)
    
    return nodes


def calculate_depth(service_name: str, nodes: Dict[str, ServiceNode]) -> int:
    """Calculate graph depth for a service"""
    service = nodes.get(service_name)
    
    if not service or not service.dependencies:
        return 1
    
    max_depth = 0
    visited = set()
    queue = [(service_name, 0)]
    
    while queue:
        current_name, depth = queue.pop(0)
        
        if current_name in visited:
            continue
        visited.add(current_name)
        max_depth = max(max_depth, depth)
        
        current = nodes.get(current_name)
        if current:
            for dep_name in current.dependencies:
                if dep_name not in visited and dep_name in nodes:
                    queue.append((dep_name, depth + 1))
    
    return max_depth + 1


def find_critical_path(services: List[ServiceTiming]) -> List[str]:
    """Find services on the critical boot path"""
    if not services:
        return []
    
    critical = []
    max_time = 0
    
    for service in services:
        path_time = calculate_path_time(service, services)
        if path_time > max_time:
            max_time = path_time
            critical = [service.name]
    
    return critical


def calculate_path_time(service: ServiceTiming,
                       all_services: List[ServiceTiming]) -> int:
    """Calculate total time for dependency chain"""
    total = service.duration_ms
    
    for dep_name in service.dependencies:
        dep = next((s for s in all_services 
                   if s.name == dep_name), None)
        if dep:
            total += calculate_path_time(dep, all_services)
    
    return total