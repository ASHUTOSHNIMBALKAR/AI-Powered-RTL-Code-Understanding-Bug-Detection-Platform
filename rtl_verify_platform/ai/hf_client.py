from typing import Dict, Any
from rtl_verify_platform.ai.base import BaseAIProvider
from rtl_verify_platform.core.config import config_manager

class HuggingFaceProvider(BaseAIProvider):
    """Local HuggingFace model client (Qwen2.5-Coder / CodeLlama)."""
    
    def __init__(self):
        self.model_name = config_manager.get("ai.local_hf_model", "Qwen/Qwen2.5-Coder-7B-Instruct")

    def explain_rtl(self, rtl_code: str) -> str:
        return f"[Local HF: {self.model_name}] RTL explanation generated."

    def detect_bugs(self, rtl_code: str, waveform_summary: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ok", "bugs": []}
