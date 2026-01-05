"""Color schemes and theming."""

from typing import Dict


COLOR_SCHEMES = {
    "default": {
        "primary": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "blue",
        "muted": "dim",
    },
    "dark": {
        "primary": "bright_cyan",
        "success": "bright_green",
        "warning": "bright_yellow",
        "error": "bright_red",
        "info": "bright_blue",
        "muted": "dim white",
    },
    "light": {
        "primary": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "info": "cyan",
        "muted": "grey50",
    },
}


def get_color_scheme(theme: str = "default") -> Dict[str, str]:
    """Get color scheme for theme."""
    return COLOR_SCHEMES.get(theme, COLOR_SCHEMES["default"])
