"""
Utility functions
"""

def format_duration(ms: float) -> str:
    """Format milliseconds like systemd-analyze: 1min 3.200s / 4.978s / 988ms"""
    if ms >= 60000:
        minutes = int(ms // 60000)
        return f"{minutes}min {(ms - minutes * 60000) / 1000:.3f}s"
    if ms >= 1000:
        return f"{ms / 1000:.3f}s"
    return f"{int(ms)}ms"


def format_duration_short(ms: int) -> str:
    """Format milliseconds (short form)"""
    return f"{ms/1000:.2f}s"


def pad_string(s: str, width: int, align: str = 'left') -> str:
    """Pad string to width"""
    if align == 'right':
        return s.rjust(width)
    else:
        return s.ljust(width)