from pathlib import Path
from enum import Enum


class DisplayMode(str, Enum):
    AUTO = "auto"
    BASEBALL = "baseball"
    NASCAR = "nascar"
    DASHBOARD = "dashboard"
    DEMO = "demo"
    MANUAL = "manual"


class PanelPriority(str, Enum):
    LIVE = "live"
    STATIC = "static"


class PanelStatus(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class ApiStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"


# File paths
STATUS_FILE = Path(__file__).parent / "data" / "display_status.json"
CONFIG_FILE = Path(__file__).parent / "data" / "config.json"

# Default configuration
DEFAULT_MODE = DisplayMode.AUTO

DEFAULT_CONFIG = {
    "devices": {
        "baseball_1": {
            "mode": DEFAULT_MODE.value,
            "live_content_timeout": 120000,  # 2 minutes in milliseconds
            "rotation_interval": 15000,  # 15 seconds in milliseconds
            "sub_panel_duration_offset": 5000,  # 5 seconds in milliseconds
            "panels": {
                "baseball": {
                    "enabled": True,
                    "duration": 30000,  # 30 seconds
                    "priority": PanelPriority.LIVE.value,
                },
                "dashboard": {
                    "enabled": True,
                    "duration": 15000,  # 15 seconds
                    "priority": PanelPriority.STATIC.value,
                },
            },
        },
        "office_display": {
            "mode": DEFAULT_MODE.value,
            "live_content_timeout": 120000,
            "rotation_interval": 15000,
            "sub_panel_duration_offset": 5000,
            "panels": {
                "baseball": {
                    "enabled": True,
                    "duration": 30000,
                    "priority": PanelPriority.LIVE.value,
                },
                "nascar": {
                    "enabled": True,
                    "duration": 45000,  # 45 seconds
                    "priority": PanelPriority.LIVE.value,
                },
                "dashboard": {
                    "enabled": True,
                    "duration": 15000,
                    "priority": PanelPriority.STATIC.value,
                },
            },
        },
        "living_room": {
            "mode": DEFAULT_MODE.value,
            "live_content_timeout": 120000,
            "rotation_interval": 15000,
            "sub_panel_duration_offset": 5000,
            "panels": {
                "baseball": {
                    "enabled": True,
                    "duration": 30000,
                    "priority": PanelPriority.LIVE.value,
                },
                "nascar": {
                    "enabled": True,
                    "duration": 45000,
                    "priority": PanelPriority.LIVE.value,
                },
                "dashboard": {
                    "enabled": True,
                    "duration": 15000,
                    "priority": PanelPriority.STATIC.value,
                },
            },
        },
    }
}
