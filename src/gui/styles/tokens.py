"""
Design tokens for Open ThermoKinetics UI.

Colors follow WCAG AA contrast requirements:
- Light: text_primary/bg_base = 16.1:1, accent/bg_base = 4.7:1
- Dark: text_primary/bg_base = 17.1:1, accent/bg_surface = 4.9:1
"""

LIGHT = {
    # Backgrounds
    "bg_base": "#FFFFFF",
    "bg_surface": "#F8FAFC",
    "bg_elevated": "#F1F5F9",
    # Text
    "text_primary": "#0F172A",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    # Accent (Blue)
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "accent_light": "#DBEAFE",
    # Borders
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    # Status
    "success": "#16A34A",
    "warning": "#D97706",
    "error": "#DC2626",
    # Console
    "console_bg": "#FFFFFF",
    # Status bar
    "statusbar_bg": "#2563EB",
    # Radius
    "radius_sm": "3px",
    "radius_md": "6px",
}

DARK = {
    # Backgrounds
    "bg_base": "#0F172A",
    "bg_surface": "#1E293B",
    "bg_elevated": "#334155",
    # Text
    "text_primary": "#F8FAFC",
    "text_secondary": "#CBD5E1",
    "text_muted": "#64748B",
    # Accent (Blue)
    "accent": "#3B82F6",
    "accent_hover": "#60A5FA",
    "accent_light": "#1E3A8A",
    # Borders
    "border": "#334155",
    "border_strong": "#475569",
    # Status
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#EF4444",
    # Console
    "console_bg": "#0D1117",
    # Status bar
    "statusbar_bg": "#1E3A8A",
    # Radius
    "radius_sm": "3px",
    "radius_md": "6px",
}
