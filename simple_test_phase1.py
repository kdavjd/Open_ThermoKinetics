#!/usr/bin/env python3
"""
Simple test for Phase 1 framework components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    try:
        import importlib.util

        # Test ContentManager
        spec = importlib.util.find_spec("src.gui.user_guide_framework.core.content_manager")
        if spec is not None:
            print("✓ ContentManager import available")
        else:
            print("✗ ContentManager import failed")
            return False

        # Test NavigationManager
        spec = importlib.util.find_spec("src.gui.user_guide_framework.core.navigation_manager")
        if spec is not None:
            print("✓ NavigationManager import available")
        else:
            print("✗ NavigationManager import failed")
            return False

        # Test ThemeManager
        spec = importlib.util.find_spec("src.gui.user_guide_framework.core.theme_manager")
        if spec is not None:
            print("✓ ThemeManager import available")
        else:
            print("✗ ThemeManager import failed")
            return False

        # Test LocalizationManager
        spec = importlib.util.find_spec("src.gui.user_guide_framework.core.localization_manager")
        if spec is not None:
            print("✓ LocalizationManager import available")
        else:
            print("✗ LocalizationManager import failed")
            return False

        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of core components"""
    print("\nTesting basic functionality...")

    try:
        from src.gui.user_guide_framework.core.content_manager import ContentManager
        from src.gui.user_guide_framework.core.localization_manager import LocalizationManager
        from src.gui.user_guide_framework.core.navigation_manager import NavigationManager
        from src.gui.user_guide_framework.core.theme_manager import ThemeManager

        # Test data directory
        data_dir = project_root / "src" / "gui" / "user_guide_framework" / "data"

        # Test ContentManager initialization
        if data_dir.exists() and (data_dir / "toc.json").exists():
            content_manager = ContentManager(data_dir)
            print("✓ ContentManager initialized with data directory")

            # Test NavigationManager
            nav_manager = NavigationManager(content_manager)
            tree_info = nav_manager.get_tree_info()
            print(f"✓ NavigationManager: {tree_info['total_nodes']} nodes loaded")
        else:
            print("! No data directory found, testing with minimal setup")

        # Test ThemeManager
        theme_manager = ThemeManager()
        primary_color = theme_manager.get_color("primary")
        print(f"✓ ThemeManager: Primary color = {primary_color.name()}")

        # Test LocalizationManager
        loc_manager = LocalizationManager()
        current_lang = loc_manager.get_current_language()
        print(f"✓ LocalizationManager: Current language = {current_lang}")

        return True

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("User Guide Framework - Phase 1 Simple Test")
    print("=" * 50)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return 1

    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed!")
        return 1

    print("\n🎉 All basic tests passed!")
    print("Phase 1 infrastructure appears to be working correctly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
