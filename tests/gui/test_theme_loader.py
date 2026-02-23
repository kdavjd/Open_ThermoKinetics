"""Tests for theme_loader: font loading, theme switching, QSettings persistence.

Stage 8 acceptance tests — verify that Source Sans 3 and JetBrains Mono fonts
load without DirectWrite errors on Windows.
"""

from pathlib import Path

import pytest

FONTS_DIR = Path(__file__).parents[2] / "src" / "gui" / "styles" / "fonts"

EXPECTED_FONTS = [
    "SourceSans3-Regular.ttf",
    "SourceSans3-Bold.ttf",
    "SourceSans3-SemiBold.ttf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold.ttf",
]


# ---------------------------------------------------------------------------
# Unit tests — no Qt required
# ---------------------------------------------------------------------------


class TestFontFiles:
    """Verify font files are valid TrueType binaries."""

    @pytest.mark.parametrize("filename", EXPECTED_FONTS)
    def test_font_file_exists(self, filename):
        """Each expected font file must exist in fonts/ directory."""
        assert (FONTS_DIR / filename).exists(), f"Missing font file: {filename}"

    @pytest.mark.parametrize("filename", EXPECTED_FONTS)
    def test_font_file_is_valid_ttf(self, filename):
        """Each font file must start with valid TrueType/OTF magic bytes.

        Valid signatures:
          00 01 00 00 — TrueType / OpenType with TTF outlines
          4F 54 54 4F — OpenType with CFF outlines (OTTO)
          74 72 75 65 — Mac TrueType ('true')
        """
        path = FONTS_DIR / filename
        with open(path, "rb") as f:
            magic = f.read(4)

        valid_signatures = {
            b"\x00\x01\x00\x00",  # TrueType
            b"OTTO",  # OpenType CFF
            b"true",  # Mac TrueType
        }
        assert magic in valid_signatures, (
            f"{filename}: invalid TTF magic {magic.hex()!r}. File is likely corrupted or a placeholder."
        )

    @pytest.mark.parametrize("filename", EXPECTED_FONTS)
    def test_font_file_is_not_empty_or_html(self, filename):
        """Font file must be at least 10 KB and not start with HTML markers."""
        path = FONTS_DIR / filename
        size = path.stat().st_size
        assert size >= 10_000, f"{filename}: too small ({size} bytes) — likely a placeholder"

        with open(path, "rb") as f:
            first_bytes = f.read(16)
        assert b"<!DOCTYPE" not in first_bytes and b"<html" not in first_bytes, (
            f"{filename}: starts with HTML — likely a 404 page downloaded by mistake"
        )


# ---------------------------------------------------------------------------
# Qt integration tests
# ---------------------------------------------------------------------------


class TestLoadFonts:
    """Verify load_fonts() registers all expected font families."""

    def test_load_fonts_returns_non_empty_dict(self, qtbot):
        """load_fonts() must return at least one loaded font."""
        from src.gui.styles.theme_loader import load_fonts

        fonts = load_fonts()
        assert isinstance(fonts, dict)
        assert len(fonts) > 0, "load_fonts() returned empty dict — no fonts loaded"

    def test_source_sans_3_family_loaded(self, qtbot):
        """'Source Sans 3' font family must be registered after load_fonts()."""
        from src.gui.styles.theme_loader import load_fonts

        fonts = load_fonts()
        families = set(fonts.values())
        assert "Source Sans 3" in families, (
            f"'Source Sans 3' not in loaded families: {families}. Check font files in src/gui/styles/fonts/."
        )

    def test_jetbrains_mono_family_loaded(self, qtbot):
        """'JetBrains Mono' font family must be registered after load_fonts()."""
        from src.gui.styles.theme_loader import load_fonts

        fonts = load_fonts()
        families = set(fonts.values())
        assert "JetBrains Mono" in families, f"'JetBrains Mono' not in loaded families: {families}"

    def test_load_fonts_no_warnings(self, qtbot, capsys):
        """load_fonts() must not print any WARNING lines — all fonts load cleanly."""
        from src.gui.styles.theme_loader import load_fonts

        load_fonts()
        captured = capsys.readouterr()
        warning_lines = [line for line in captured.out.splitlines() if "WARNING" in line]
        assert not warning_lines, "Font loading produced warnings (DirectWrite error?):\n" + "\n".join(warning_lines)

    def test_all_source_sans_3_files_load(self, qtbot):
        """All three Source Sans 3 variants must load successfully."""
        from src.gui.styles.theme_loader import load_fonts

        fonts = load_fonts()
        source_sans_keys = [k for k in fonts if "SourceSans3" in k]
        assert len(source_sans_keys) >= 3, (
            f"Expected 3 Source Sans 3 entries, got {len(source_sans_keys)}: {source_sans_keys}"
        )


class TestLoadTheme:
    """Verify load_theme() applies styles without errors."""

    def test_load_dark_theme(self, qtbot):
        """load_theme('dark') must apply stylesheet without exceptions."""
        from PyQt6.QtWidgets import QApplication

        from src.gui.styles.theme_loader import load_theme

        app = QApplication.instance()
        load_theme(app, "dark")
        assert len(app.styleSheet()) > 0

    def test_load_light_theme(self, qtbot):
        """load_theme('light') must apply stylesheet without exceptions."""
        from PyQt6.QtWidgets import QApplication

        from src.gui.styles.theme_loader import load_theme

        app = QApplication.instance()
        load_theme(app, "light")
        assert len(app.styleSheet()) > 0

    def test_get_saved_theme_returns_valid_string(self, qtbot):
        """get_saved_theme() must return 'light' or 'dark'."""
        from src.gui.styles.theme_loader import get_saved_theme

        theme = get_saved_theme()
        assert theme in ("light", "dark"), f"Unexpected theme: {theme!r}"

    def test_load_theme_persists_before_setStyleSheet(self, qtbot, mocker):
        """QSettings must be saved BEFORE app.setStyleSheet() to prevent changeEvent desync.

        Bug: setStyleSheet() delivers QEvent.StyleChange synchronously; if the theme is
        saved AFTER setStyleSheet, PlotCanvas.changeEvent fires with get_saved_theme()
        returning the OLD value (anti-phase bug).
        """
        from PyQt6.QtCore import QSettings
        from PyQt6.QtWidgets import QApplication

        from src.gui.styles.theme_loader import load_theme

        app = QApplication.instance()

        saved_at_stylesheet_time = []

        original_set_stylesheet = app.setStyleSheet

        def intercept_set_stylesheet(qss):
            settings = QSettings("OpenThermoKinetics", "App")
            saved_at_stylesheet_time.append(settings.value("theme", "unknown"))
            original_set_stylesheet(qss)

        mocker.patch.object(app, "setStyleSheet", side_effect=intercept_set_stylesheet)

        load_theme(app, "dark")

        assert saved_at_stylesheet_time == ["dark"], (
            "Theme was not persisted to QSettings before app.setStyleSheet() was called. "
            "This causes changeEvent to apply the wrong theme (anti-phase desync)."
        )

    def test_load_theme_switch_sequence_no_desync(self, qtbot):
        """Repeated theme switches must always save the correct theme.

        Verifies that after each load_theme() call, get_saved_theme() reflects
        the requested theme — no off-by-one residue from the previous call.
        """
        from PyQt6.QtWidgets import QApplication

        from src.gui.styles.theme_loader import get_saved_theme, load_theme

        app = QApplication.instance()

        for expected in ("dark", "light", "dark", "light"):
            load_theme(app, expected)
            actual = get_saved_theme()
            assert actual == expected, f"After load_theme({expected!r}), get_saved_theme() returned {actual!r}"
