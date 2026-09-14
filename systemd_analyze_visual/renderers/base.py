"""
Base renderer class
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from abc import ABC, abstractmethod
from systemd_analyze_visual.models import BootMetrics


class BaseRenderer(ABC):
    """Base class for all renderers"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    @abstractmethod
    def render(self, metrics: BootMetrics) -> str:
        """Render boot metrics"""
        pass