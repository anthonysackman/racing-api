import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .constants import CONFIG_FILE, DEFAULT_CONFIG, DisplayMode, PanelPriority


class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                # Merge with defaults to ensure all fields exist
                return self._merge_with_defaults(config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}, using defaults")
                return DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all fields exist"""
        merged = DEFAULT_CONFIG.copy()

        # Merge top-level fields
        for key, value in config.items():
            if key == "panels":
                # Merge panel configurations
                for panel_name, panel_config in value.items():
                    if panel_name in merged["panels"]:
                        merged["panels"][panel_name].update(panel_config)
                    else:
                        merged["panels"][panel_name] = panel_config
            else:
                merged[key] = value

        # Merge devices
        if "devices" in config:
            for device_id, device_config in config["devices"].items():
                if device_id not in merged["devices"]:
                    merged["devices"][device_id] = device_config
                else:
                    # Merge device config fields
                    for key, value in device_config.items():
                        if key == "panels":
                            for panel_name, panel_config in value.items():
                                if panel_name in merged["devices"][device_id]["panels"]:
                                    merged["devices"][device_id]["panels"][
                                        panel_name
                                    ].update(panel_config)
                                else:
                                    merged["devices"][device_id]["panels"][
                                        panel_name
                                    ] = panel_config
                        else:
                            merged["devices"][device_id][key] = value
        return merged

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def get_device_config(self, device_id: str) -> Dict[str, Any]:
        """Get configuration for a specific device"""
        # Fallback to 'baseball_1' if device_id not found
        return self.config["devices"].get(device_id) or self.config["devices"].get(
            "baseball_1"
        )

    def update_device_config(self, device_id: str, updates: Dict[str, Any]) -> bool:
        """Update configuration for a specific device"""
        if device_id not in self.config["devices"]:
            self.config["devices"][device_id] = {}
        self._deep_merge(self.config["devices"][device_id], updates)
        return self._save_config(self.config)

    def get_all_devices(self) -> Dict[str, Any]:
        """Get all device configurations"""
        return self.config["devices"]

    def get_mode(self) -> str:
        """Get current display mode"""
        return self.config.get("mode", DEFAULT_CONFIG["mode"])

    def set_mode(self, mode: str) -> bool:
        """Set display mode"""
        try:
            DisplayMode(mode)  # Validate mode
            self.config["mode"] = mode
            return self._save_config(self.config)
        except ValueError:
            return False

    def get_panel_config(self, panel_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific panel"""
        return self.config.get("panels", {}).get(panel_name)

    def update_panel_config(
        self, panel_name: str, panel_config: Dict[str, Any]
    ) -> bool:
        """Update configuration for a specific panel"""
        if "panels" not in self.config:
            self.config["panels"] = {}

        if panel_name not in self.config["panels"]:
            self.config["panels"][panel_name] = {}

        self.config["panels"][panel_name].update(panel_config)
        return self._save_config(self.config)

    def get_timing_config(self) -> Dict[str, int]:
        """Get timing-related configuration"""
        return {
            "live_content_timeout": self.config.get(
                "live_content_timeout", DEFAULT_CONFIG["live_content_timeout"]
            ),
            "rotation_interval": self.config.get(
                "rotation_interval", DEFAULT_CONFIG["rotation_interval"]
            ),
            "sub_panel_duration_offset": self.config.get(
                "sub_panel_duration_offset", DEFAULT_CONFIG["sub_panel_duration_offset"]
            ),
        }

    def update_timing_config(self, timing_config: Dict[str, int]) -> bool:
        """Update timing-related configuration"""
        for key, value in timing_config.items():
            if key in [
                "live_content_timeout",
                "rotation_interval",
                "sub_panel_duration_offset",
            ]:
                self.config[key] = value
        return self._save_config(self.config)

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Recursively merge source into target"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


# Global config manager instance
config_manager = ConfigManager()
