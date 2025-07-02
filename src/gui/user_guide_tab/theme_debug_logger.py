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
    # Table width calculation: 16+16+12+8 + separators = 68 chars
    table_width = 68
    logger.info("=" * table_width)
    logger.info(f"THEME COLORS DEBUG TABLE - Theme: '{theme_name}'")
    logger.info("=" * table_width)

    # Get all colors from current theme
    colors = theme_manager.current_theme.get("colors", {})

    if not colors:
        logger.warning("No colors found in theme!")
        return

    # Header with proper column widths
    logger.info(f"{'Color Key':<16} | {'Theme Value':<16} | {'QColor':<12} | {'Status':<8}")
    logger.info("-" * table_width)

    # Log each color available in theme
    for color_key, color_value in colors.items():
        try:
            qcolor = theme_manager.get_color(color_key)
            is_valid = "✓ Valid" if qcolor.isValid() else "✗ Invalid"
            value_str = str(color_value)[:16]  # Truncate to fit column
            qcolor_str = qcolor.name()[:12]  # Truncate to fit column
            logger.info(f"{color_key:<16} | {value_str:<16} | {qcolor_str:<12} | {is_valid:<8}")
        except Exception as e:
            error_str = str(e)[:8]  # Truncate error message
            logger.error(f"{color_key:<16} | {str(color_value)[:16]:<16} | ERROR:{error_str:<7} | ✗")

    logger.info("-" * table_width)

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
    logger.info("-" * table_width)

    for key in common_requests:
        try:
            color = theme_manager.get_color(key)
            if key in colors:
                status = "✓ Found"
                expected = str(colors[key])[:16]
            else:
                status = "✗ Missing"
                expected = "N/A (fallback)"

            color_str = color.name()[:12]  # Truncate to fit column
            logger.info(f"{key:<16} | {expected:<16} | {color_str:<12} | {status:<8}")
        except Exception as e:
            error_str = str(e)[:8]  # Truncate error message
            logger.error(f"{key:<16} | ERROR:{error_str:<11} | | ✗")

    logger.info("=" * table_width)


def log_component_theme_application(component_name: str, color_requests: list, theme_manager) -> None:
    """
    Log what colors a specific component is requesting and their results.

    Args:
        component_name: Name of the component
        color_requests: List of color keys the component is requesting
        theme_manager: ThemeManager instance
    """
    # Use shorter table for component application
    table_width = 60
    logger.info(f"COMPONENT THEME APPLICATION: {component_name}")
    logger.info("-" * table_width)

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

            # Truncate values to fit properly
            expected_str = str(expected)[:15]
            color_str = color.name()[:10]
            logger.info(f"  {color_key:<20} | Expected: {expected_str:<15} | Got: {color_str:<10} | {status}")

        except Exception as e:
            logger.error(f"  {color_key:<20} | ERROR: {e}")

    logger.info("-" * table_width)
