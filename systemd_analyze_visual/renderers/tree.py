"""
Tree format renderer
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Set
from systemd_analyze_visual.models import ProcessedService, BootMetrics
from systemd_analyze_visual.renderers.colors import Colors, TreeChars

class TreeRenderer:
    """Render services as dependency tree"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.visited = set()
    
    def render(self, metrics: BootMetrics, max_depth: int = 5) -> str:
        """Render boot metrics as tree"""
        lines = []
        
        # Group by severity
        by_severity = {
            'CRITICAL': [],
            'ORANGE': [],
            'WARN': [],
            'OK': []
        }
        
        for service in metrics.services:
            by_severity[service.severity].append(service)
        
        # Render each severity group
        for severity in ['CRITICAL', 'ORANGE', 'WARN']:
            if by_severity[severity]:
                lines.append(f"\n{severity} Services ({len(by_severity[severity])}):")
                for svc in by_severity[severity][:10]:
                    lines.append(self._format_node(svc, indent=2))
        
        return "\n".join(lines)
    
    def _format_node(self, service: ProcessedService, 
                    indent: int = 0) -> str:
        """Format single node in tree"""
        prefix = " " * indent
        
        if self.use_colors:
            color = Colors.severity_color(service.severity)
            reset = Colors.RESET
        else:
            color = reset = ""
        
        time_str = f"({service.duration_ms/1000:.2f}s)"
        
        return f"{prefix}{color}● {service.name}{reset} {time_str}"
    
    def render_dependency_tree(self, metrics: BootMetrics) -> str:
        """Render full dependency tree"""
        lines = []
        lines.append("Boot dependency tree:")
        lines.append("")
        
        # Find root (systemd.special or first service)
        root = next((s for s in metrics.services 
                    if s.name == 'systemd.special'), None)
        
        if root:
            self.visited = set()
            lines.append(self._render_node_recursive(root, metrics, 0))
        
        return "\n".join(lines)
    
    def _render_node_recursive(self, service: ProcessedService,
                              metrics: BootMetrics,
                              depth: int, is_last: bool = True) -> str:
        """Recursively render node and children"""
        if service.name in self.visited or depth > 5:
            return ""
        
        self.visited.add(service.name)
        
        lines = []
        
        # Format current node
        if depth == 0:
            prefix = ""
        else:
            prefix = (TreeChars.LAST if is_last else TreeChars.BRANCH)
        
        if self.use_colors:
            color = Colors.severity_color(service.severity)
            reset = Colors.RESET
        else:
            color = reset = ""
        
        indent = "  " * (depth + 1)
        time_str = f"({service.duration_ms/1000:.2f}s)"
        lines.append(f"{indent}{prefix}{color}{service.name}{reset} {time_str}")
        
        # Render children
        children = [s for s in metrics.services 
                   if service.name in s.dependencies]
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            child_lines = self._render_node_recursive(
                child, metrics, depth + 1, is_last_child
            )
            if child_lines:
                lines.append(child_lines)
        
        return "\n".join(lines)