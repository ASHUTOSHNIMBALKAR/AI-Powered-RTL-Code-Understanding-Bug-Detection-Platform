from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAIProvider(ABC):
    """Abstract base class for RTL AI understanding and bug detection providers."""
    
    @abstractmethod
    def explain_rtl(self, rtl_code: str) -> str:
        """Generates natural language explanation of the RTL module."""
        pass

    @abstractmethod
    def detect_bugs(self, rtl_code: str, waveform_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Identifies potential RTL synthesis and timing bugs."""
        pass
