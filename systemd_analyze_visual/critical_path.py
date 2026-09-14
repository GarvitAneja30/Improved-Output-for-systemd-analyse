"""
Parse systemd critical chain to find real bottlenecks
"""

import sys
import os
import subprocess
import re
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systemd_analyze_visual.models import ServiceTiming

def get_critical_chain() -> str:
    """Get raw critical-chain output from systemd-analyze"""
    try:
        result = subprocess.run(
            ['systemd-analyze', 'critical-chain'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        print(f"Error getting critical-chain: {e}", file=sys.stderr)
        return ""


def parse_critical_chain(chain_output: str) -> List[Tuple[str, float]]:
    """
    Parse critical-chain output to extract service path and times
    
    Returns: List of (service_name, duration_ms) tuples in order
    """
    services = []
    lines = chain_output.strip().split('\n')
    
    for line in lines:
        # Skip empty lines and header
        if not line.strip() or 'The time' in line:
            continue
        
        # Parse lines like: "└─NetworkManager.service @4.502s +3.285s"
        # Extract service name and duration
        match = re.search(r'([\w\-\.]+\.(?:service|target|socket))\s+@([\d.]+)s\s+\+([\d.]+)s', line)
        if match:
            service_name = match.group(1)
            start_time = float(match.group(2))
            duration = float(match.group(3))
            
            services.append((service_name, duration * 1000))  # Convert to ms
    
    return services


def identify_critical_path_services(chain_output: str) -> Dict[str, Dict]:
    """
    Parse critical chain and identify which services are on critical path
    
    Returns: Dict with service info including whether it's on critical path
    """
    critical_services = {}
    services = parse_critical_chain(chain_output)
    
    for service_name, duration_ms in services:
        critical_services[service_name] = {
            'duration_ms': duration_ms,
            'on_critical_path': True,
            'blocks_boot': True
        }
    
    return critical_services


def mark_parallel_services(critical_services: Dict, all_services: List[ServiceTiming]) -> Dict:
    """
    Mark services that run in parallel (not on critical path) as non-blocking
    """
    critical_names = set(critical_services.keys())
    
    for service in all_services:
        if service.name not in critical_names:
            critical_services[service.name] = {
                'duration_ms': service.duration_ms,
                'on_critical_path': False,
                'blocks_boot': False,
                'note': 'Runs in parallel - does not block boot'
            }
    
    return critical_services