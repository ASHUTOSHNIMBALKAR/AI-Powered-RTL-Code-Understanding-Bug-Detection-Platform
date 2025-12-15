from typing import List, Dict, Any

class GlitchDetector:
    """Detects signal glitches and race conditions below threshold duration."""
    
    def __init__(self, threshold_ns: float = 0.1):
        self.threshold_ns = threshold_ns

    def analyze_signal(self, signal_name: str, transitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        glitches = []
        for i in range(len(transitions) - 1):
            delta = transitions[i+1]["time"] - transitions[i]["time"]
            if delta < self.threshold_ns:
                glitches.append({
                    "signal": signal_name,
                    "time": transitions[i]["time"],
                    "duration": delta
                })
        return glitches
