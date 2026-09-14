"""
Command-line interface and argument parsing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse

from systemd_analyze_visual.collector import collect_timings
from systemd_analyze_visual.processor import process_timings
from systemd_analyze_visual.filters import apply_filters, FilterCriteria, sort_services
from systemd_analyze_visual.renderers import TableRenderer, TreeRenderer, LegacyRenderer
from systemd_analyze_visual.renderers.colors import Colors

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='Enhanced systemd-analyze with visual output',
        prog='systemd-analyze-visual'
    )
    
    parser.add_argument('--table', action='store_true',
                       help='Show table view (default)')
    parser.add_argument('--tree', action='store_true',
                       help='Show tree view')
    parser.add_argument('--legacy', '--blame', action='store_true',
                       help='Show original blame format')
    
    parser.add_argument('--min-time', type=float, default=0,
                       help='Filter: only services > time (seconds)')
    parser.add_argument('--max-time', type=float, default=999999,
                       help='Filter: only services < time (seconds)')
    
    parser.add_argument('--severity', choices=['ok', 'warn', 'orange', 
                                              'critical', 'slow', 'problem'],
                       help='Filter by severity')
    
    parser.add_argument('--service', '--name', type=str,
                       help='Filter by service name (regex)')
    
    parser.add_argument('--dependency', type=str,
                       help='Show services related to dependency')
    
    parser.add_argument('--sort', choices=['time', 'name', 'severity', 'depth'],
                       default='time',
                       help='Sort by: time, name, severity, depth')
    
    parser.add_argument('--summary', action='store_true',
                       help='Show boot summary')
    
    parser.add_argument('--bottlenecks', action='store_true',
                       help='Show main bottlenecks')
    
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
    parser.add_argument('--limit', type=int, default=20,
                       help='Limit number of services shown')
    
    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Collect timing data
    print("Collecting boot timing data...", file=sys.stderr)
    raw_timings = collect_timings()
    
    if not raw_timings:
        print("Error: No timing data available. "
              "Try running with sudo?", file=sys.stderr)
        return 1
    
    # Process data
    metrics = process_timings(raw_timings)
    
    # Apply filters
    filters = FilterCriteria(
        min_time_s=args.min_time,
        max_time_s=args.max_time,
        severity=args.severity,
        name_pattern=args.service,
        dependency=args.dependency
    )
    metrics = apply_filters(metrics, filters)
    
    # Sort
    metrics.services = sort_services(metrics.services, 
                                    sort_key=args.sort)
    
    # Render
    use_colors = not args.no_color
    
    if args.legacy:
        renderer = LegacyRenderer()
        output = renderer.render(metrics.services)
    elif args.tree:
        renderer = TreeRenderer(use_colors=use_colors)
        output = renderer.render(metrics)
    else:
        renderer = TableRenderer(use_colors=use_colors)
        output = renderer.render(metrics, limit=args.limit)
    
    # Add optional sections
    if args.summary or args.bottlenecks:
        if isinstance(renderer, TableRenderer):
            if args.summary:
                output += renderer.render_summary(metrics)
            if args.bottlenecks:
                output += renderer.render_bottlenecks(metrics)
    
    # Strip colors if requested
    if args.no_color:
        output = Colors.strip_ansi(output)
    
    print(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())