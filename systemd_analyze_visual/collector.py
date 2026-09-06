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
        # Get all units
        units = manager.ListUnits()
        
        for unit_info in units:
            name, desc, load_state, active_state, sub_state, \
            following, obj_path, job_type, job_path, job_timeout = unit_info
            
            # Filter: only services and targets
            if not (name.endswith('.service') or name.endswith('.target')):
                continue
            
            # Get unit object
            try:
                unit_obj = bus.get_object('org.freedesktop.systemd1', obj_path)
                unit_props = dbus.Interface(
                    unit_obj,
                    'org.freedesktop.DBus.Properties'
                )
                
                # Get all properties for this unit
                props = unit_props.GetAll('org.freedesktop.systemd1.Unit')
                
                # Extract timing data
                start_time = props.get('ActiveEnterTimestampMonotonic', 0)
                finish_time = props.get('ActiveExitTimestampMonotonic', 0)
                
                # If not active yet, use current timestamp
                if finish_time == 0:
                    finish_time = start_time
                
                duration = max(0, finish_time - start_time)
                
                # Extract dependencies
                requires = props.get('Requires', [])
                wants = props.get('Wants', [])
                dependencies = list(set(requires + wants))
                
                wanted_by = props.get('WantedBy', [])
                
                service = ServiceTiming(
                    name=name,
                    duration_ms=duration,
                    start_time_ms=start_time,
                    state=active_state,
                    dependencies=dependencies,
                    wanted_by=wanted_by
                )
                
                services.append(service)
            
            except Exception as e:
                # Skip services we can't read
                continue
        
        return services
    
    except dbus.exceptions.DBusException as e:
        print(f"Error: Failed to list units: {e}", file=sys.stderr)
        return []