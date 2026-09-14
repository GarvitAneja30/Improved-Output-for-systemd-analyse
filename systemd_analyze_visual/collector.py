"""
D-Bus data collection from systemd
"""

import dbus
import sys
from typing import List
from .models import ServiceTiming

def get_dbus_connection():
    """Get D-Bus system connection"""
    try:
        return dbus.SystemBus()
    except dbus.exceptions.DBusException as e:
        print(f"Error: Cannot connect to D-Bus: {e}", file=sys.stderr)
        return None


def get_manager_interface(bus):
    """Get systemd manager interface"""
    try:
        systemd1 = bus.get_object('org.freedesktop.systemd1',
                                  '/org/freedesktop/systemd1')
        return dbus.Interface(systemd1,
                            'org.freedesktop.systemd1.Manager')
    except dbus.exceptions.DBusException as e:
        print(f"Error: Cannot get systemd manager: {e}", file=sys.stderr)
        return None


def collect_timings() -> List[ServiceTiming]:
    """Collect boot timing data from D-Bus"""
    bus = get_dbus_connection()
    if not bus:
        return []
    
    manager = get_manager_interface(bus)
    if not manager:
        return []
    
    services = []
    
    try:
        units = manager.ListUnits()
        
        for unit_info in units:
            name, desc, load_state, active_state, sub_state, \
            following, obj_path, job_type, job_path, job_timeout = unit_info
            
            if not (name.endswith('.service') or name.endswith('.target')):
                continue
            
            try:
                unit_obj = bus.get_object('org.freedesktop.systemd1', obj_path)
                unit_props = dbus.Interface(
                    unit_obj,
                    'org.freedesktop.DBus.Properties'
                )
                
                props = unit_props.GetAll('org.freedesktop.systemd1.Unit')
                
                # Get timing - use InactiveExitTimestamp instead
                start_time = props.get('InactiveExitTimestampMonotonic', 0)
                finish_time = props.get('ActiveEnterTimestampMonotonic', 0)
                
                # If both are 0, service hasn't started
                if start_time == 0 and finish_time == 0:
                    continue
                
                duration = max(0, finish_time - start_time)
                
                # Get FULL dependency info
                requires = props.get('Requires', [])
                wants = props.get('Wants', [])
                before = props.get('Before', [])  # NEW
                after = props.get('After', [])    # NEW
                
                dependencies = list(set(requires + wants + after))
                wanted_by = list(set(before))
                
                service = ServiceTiming(
                    name=name,
                    duration_ms=int(duration),
                    start_time_ms=int(start_time),
                    state=active_state,
                    dependencies=dependencies,
                    wanted_by=wanted_by
                )
                
                services.append(service)
            
            except Exception as e:
                continue
        
        return services
    
    except Exception as e:
        print(f"Error: Failed to list units: {e}", file=sys.stderr)
        return []