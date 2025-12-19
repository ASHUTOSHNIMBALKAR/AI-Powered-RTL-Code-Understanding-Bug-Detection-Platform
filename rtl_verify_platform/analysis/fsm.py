import re
from typing import Set

class FSMExtractor:
    """Extracts Finite State Machine states and transitions from Verilog RTL."""
    
    def __init__(self, verilog_content: str):
        self.content = verilog_content
        self.states: Set[str] = set()

    def extract_states(self) -> Set[str]:
        pattern = re.compile(r"(?:parameter|localparam)\s+.*?(\b[A-Z0-9_]+\b)\s*=\s*\d+'[bdh][0-9a-fA-F]+", re.IGNORECASE)
        for match in pattern.finditer(self.content):
            self.states.add(match.group(1))
        return self.states
