import re
from pathlib import Path
from typing import Dict, List, Any

class VCDParser:
    """Parses VCD (Value Change Dump) files into structured transition timelines."""
    
    def __init__(self, vcd_path: str | Path):
        self.vcd_path = Path(vcd_path)
        self.signals: Dict[str, Dict[str, Any]] = {}
        self.transitions: List[Dict[str, Any]] = []

    def parse(self) -> Dict[str, Any]:
        if not self.vcd_path.exists():
            return {"signals": {}, "transitions": []}
            
        with open(self.vcd_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        var_pattern = re.compile(r"\$var\s+(\w+)\s+(\d+)\s+(\S+)\s+(\w+)\s+\$end")
        for match in var_pattern.finditer(content):
            var_type, size, symbol, name = match.groups()
            self.signals[symbol] = {
                "name": name,
                "type": var_type,
                "size": int(size)
            }

        return {
            "signals": self.signals,
            "signal_count": len(self.signals)
        }
