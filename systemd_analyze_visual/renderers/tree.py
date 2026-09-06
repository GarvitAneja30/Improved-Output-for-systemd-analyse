"""
Table format renderer
"""

from typing import List
from ..models import ProcessedService, BootMetrics
from .colors import Colors

class TableRenderer:
    """Render services as formatted table"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    def render(self, metrics: BootMetrics, limit: int = 20) -> str:
        """Render boot metrics as table"""
        lines = []
        
        # Header
        lines.append(self._format_header())
        lines.append("─" * 75)
        
        # Services (limit to top N)
        services_to_show = metrics.services[:limit]
        for service in services_to_show:
            lines.append(self._format_row(service))
        
        return "\n".join(lines)
    
    def _format_header(self) -> str:
        """Format table header"""
        return f"{'SERVICE':<40} {'DURATION':<12} {'SEVERITY':<15}"
    
    def _format_row(self, service: ProcessedService) -> str:
        """Format single service row"""
        time_str = f"{service.duration_ms/1000:.2f}s"
        
        # Color the severity
        if self.use_colors:
            color = Colors.severity_color(service.severity)
            severity_str = f"{color}{service.severity:<10}{Colors.RESET}"
        else:
            severity_str = service.severity
        
        return f"{service.name:<40} {time_str:>10}s  {severity_str}"
    
    def render_summary(self, metrics: BootMetrics) -> str:
        """Render boot summary"""
        lines = []
        lines.append("\n" + "="*75)
        lines.append(f"Total boot time: {metrics.total_boot_s:.2f}s")
        lines.append(f"Kernel time: {metrics.kernel_time_ms/1000:.2f}s")
        lines.append(f"Userspace time: {metrics.userspace_time_ms/1000:.2f}s")
        lines.append(f"Services analyzed: {len(metrics.services)}")
        lines.append(f"Critical bottlenecks: {metrics.critical_count}")
        lines.append(f"Slow services: {metrics.warning_count}")
        lines.append("="*75)
        return "\n".join(lines)
    
    def render_bottlenecks(self, metrics: BootMetrics) -> str:
        """Show main bottlenecks"""
        bottlenecks = [s for s in metrics.services 
                      if s.severity in ['ORANGE', 'CRITICAL']]
        
        if not bottlenecks:
            return ""
        
        lines = []
        lines.append("\nMain bottlenecks:")
        for svc in bottlenecks[:5]:
            color = Colors.severity_color(svc.severity) if self.use_colors else ""
            reset = Colors.RESET if self.use_colors else ""
            lines.append(f"  {color}● {svc.name} ({svc.duration_ms/1000:.2f}s){reset}")
        
        return "\n".join(lines)