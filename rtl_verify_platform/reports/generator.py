from pathlib import Path
from typing import Dict, Any
import json
from rtl_verify_platform.core.config import config_manager

class ReportGenerator:
    """Generates HTML and JSON verification summary reports."""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or config_manager.get("reports.output_dir", "reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(self, run_data: Dict[str, Any], filename: str = "report.json") -> Path:
        out_path = self.output_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=2)
        return out_path
