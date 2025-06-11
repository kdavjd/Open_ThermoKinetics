"""
Theme Debug Logger - Utility for logging detailed theme information
"""

from src.core.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


def log_theme_colors_table(theme_manager, theme_name: str) -> None:
    """
    Log a detailed table of theme colors for debugging.

    Args:
        theme_manager: ThemeManager instance
        theme_name: Name of the current theme
    """
    logger.info("=" * 80)
    logger.info(f"THEME COLORS DEBUG TABLE - Theme: '{theme_name}'")
    logger.info("=" * 80)

    # Get all colors from current theme
    colors = theme_manager.current_theme.get("colors", {})

    if not colors:
        logger.warning("No colors found in theme!")
        return

    # Header
    logger.info(f"{'Color Key':<20} | {'Theme Value':<20} | {'QColor Result':<15} | {'Status':<10}")
    logger.info("-" * 80)

    # Log each color available in theme
    for color_key, color_value in colors.items():
        try:
            qcolor = theme_manager.get_color(color_key)
            is_valid = "✓ Valid" if qcolor.isValid() else "✗ Invalid"
            value_str = str(color_value)[:20]  # Truncate long values
            logger.info(f"{color_key:<20} | {value_str:<20} | {qcolor.name():<15} | {is_valid:<10}")
        except Exception as e:
            logger.error(f"{color_key:<20} | {str(color_value):<20} | ERROR: {str(e)[:10]}")

    logger.info("-" * 80)

    # Test commonly requested colors that components might be looking for
    common_requests = [
        "background_primary",
        "background_secondary",
        "background",
        "text_primary",
        "text_secondary",
        "text",
        "primary",
        "secondary",
        "accent",
        "surface",
        "border",
    ]

    logger.info("COMPONENT COLOR REQUESTS TEST:")
    logger.info("-" * 80)

    for key in common_requests:
        try:
            color = theme_manager.get_color(key)
            if key in colors:
                status = "✓ Found"
                expected = str(colors[key])[:20]
            else:
                status = "✗ Missing"
                expected = "N/A (fallback #000000)"

            logger.info(f"{key:<20} | {expected:<20} | {color.name():<15} | {status}")
        except Exception as e:
            logger.error(f"{key:<20} | ERROR: {str(e)}")

    logger.info("=" * 80)


def log_component_theme_application(component_name: str, color_requests: list, theme_manager) -> None:
    """
    Log what colors a specific component is requesting and their results.

    Args:
        component_name: Name of the component
        color_requests: List of color keys the component is requesting
        theme_manager: ThemeManager instance
    """
    logger.info(f"COMPONENT THEME APPLICATION: {component_name}")
    logger.info("-" * 60)

    colors = theme_manager.current_theme.get("colors", {})

    for color_key in color_requests:
        try:
            color = theme_manager.get_color(color_key)

            if color_key in colors:
                status = "✓ Found in theme"
                expected = colors[color_key]
            else:
                status = "✗ Missing (using fallback)"
                expected = "#000000"

            logger.info(f"  {color_key:<20} | Expected: {str(expected):<15} | Got: {color.name():<10} | {status}")

        except Exception as e:
            logger.error(f"  {color_key:<20} | ERROR: {e}")

    logger.info("-" * 60)
