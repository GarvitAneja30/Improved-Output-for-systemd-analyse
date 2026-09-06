"""
ANSI color codes and styling
"""

class Colors:
    """ANSI color codes"""
    
    # Severity colors
    OK = '\033[92m'           # Green
    WARN = '\033[93m'         # Yellow
    ORANGE = '\033[38;5;208m' # Orange
    CRITICAL = '\033[91m'     # Red
    
    # Other colors
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def severity_color(severity: str) -> str:
        """Get color for severity level"""
        colors = {
            'OK': Colors.OK,
            'WARN': Colors.WARN,
            'ORANGE': Colors.ORANGE,
            'CRITICAL': Colors.CRITICAL,
        }
        return colors.get(severity, Colors.GRAY)
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove ANSI codes from text"""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)


class TreeChars:
    """Tree drawing characters"""
    BRANCH = '├─'
    LAST = '└─'
    VERTICAL = '│'
    SPACE = '  '
    
    # Unicode alternatives
    BRANCH_UTF8 = '├─'
    LAST_UTF8 = '└─'