from pathlib import Path
from enum import Enum


class DisplayMode(str, Enum):
    ALL = "all"
    BASEBALL = "baseball"
    NASCAR = "nascar"


STATUS_FILE = Path(__file__).parent / "data" / "display_status.json"
DEFAULT_MODE = DisplayMode.ALL
