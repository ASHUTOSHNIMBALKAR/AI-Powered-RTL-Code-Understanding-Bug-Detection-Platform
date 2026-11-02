import os
from pathlib import Path
from typing import Any, Dict
import yaml
from rtl_verify_platform.core.logger import logger

DEFAULT_CONFIG_PATH = Path(__file__).parents[2] / "configs" / "default_config.yaml"

class ConfigManager:
    """Manages system configuration loading, merging, and access."""
    def __init__(self, config_path: str | Path = DEFAULT_CONFIG_PATH):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration from YAML file and falls back/merges defaults if missing."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, trying fallback default.")
            if DEFAULT_CONFIG_PATH.exists():
                self.config_path = DEFAULT_CONFIG_PATH
            else:
                logger.error("Default config file is missing!")
                self.config = {}
                return

        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
                logger.debug(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to parse config file: {e}")
            self.config = {}

    def get(self, key_path: str, default: Any = None) -> Any:
        """Retrieves config value by dot-notation path (e.g. 'simulator.verilator_path')."""
        keys = key_path.split(".")
        val: Any = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value: Any) -> None:
        """Dynamically sets/overrides configuration values."""
        keys = key_path.split(".")
        val: Any = self.config
        for k in keys[:-1]:
            if k not in val or not isinstance(val[k], dict):
                val[k] = {}
            val = val[k]
        val[keys[-1]] = value

# Global config instance
config_manager = ConfigManager()
