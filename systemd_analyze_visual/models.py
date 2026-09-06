"""
Data models for boot timing analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ServiceTiming:
    """Raw timing data for a single service"""
    name: str
    duration_ms: int          # milliseconds
    start_time_ms: int        # monotonic time
    state: str                # active, failed, skipped
    dependencies: List[str]   # Required services
    wanted_by: List[str]      # Services that want this
    
    @property
    def duration_s(self) -> float:
        """Duration in seconds"""
        return self.duration_ms / 1000.0
    
    @property
    def severity(self) -> str:
        """Severity level based on duration"""
        if self.duration_ms < 100:
            return "OK"
        elif self.duration_ms < 1000:
            return "WARN"
        elif self.duration_ms < 5000:
            return "ORANGE"
        else:
            return "CRITICAL"


@dataclass
class ProcessedService:
    """Service data after processing"""
    name: str
    duration_ms: int
    start_time_ms: int
    severity: str              # OK, WARN, ORANGE, CRITICAL
    block_count: int           # Services blocked by this
    parallel_count: int        # Services running concurrently
    depth: int                 # Graph depth from root
    dependencies: List[str]
    reverse_deps: List[str]


@dataclass
class BootMetrics:
    """Overall boot metrics"""
    total_boot_ms: int
    kernel_time_ms: int        # Time before systemd
    userspace_time_ms: int     # systemd + services
    services: List[ProcessedService]
    critical_path: List[str]
    
    @property
    def total_boot_s(self) -> float:
        return self.total_boot_ms / 1000.0
    
    @property
    def critical_count(self) -> int:
        return len([s for s in self.services 
                   if s.severity == "CRITICAL"])
    
    @property
    def warning_count(self) -> int:
        return len([s for s in self.services 
                   if s.severity in ["WARN", "ORANGE", "CRITICAL"]])


@dataclass
class ServiceNode:
    """Node in dependency graph"""
    name: str
    duration_ms: int
    dependencies: List[str]
    reverse_deps: List[str]
    depth: int = 0
    x: int = 0                 # For layout
    y: int = 0