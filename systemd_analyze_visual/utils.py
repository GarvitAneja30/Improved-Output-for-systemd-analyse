"""
Utility functions
"""

def format_duration(ms: int) -> str:
    """Format milliseconds as human readable"""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms/1000:.2f}s"
    else:
        minutes = ms / 60000
        return f"{minutes:.2f}m"


def format_duration_short(ms: int) -> str:
    """Format milliseconds (short form)"""
    return f"{ms/1000:.2f}s"


def pad_string(s: str, width: int, align: str = 'left') -> str:
    """Pad string to width"""
    if align == 'right':
        return s.rjust(width)
    else:
        return s.ljust(width)