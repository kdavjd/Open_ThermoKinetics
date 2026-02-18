# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Base directory
base_dir = Path('.')

# Data files to include
datas = [
    # User guide framework data
    ('src/gui/user_guide_tab/user_guide_framework/data', 'src/gui/user_guide_tab/user_guide_framework/data'),
    # Resources (CSV, JSON presets)
    ('resources', 'resources'),
]

# Collect scienceplots data
datas += collect_data_files('scienceplots')

a = Analysis(
    ['src/gui/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'matplotlib.backends.backend_qtagg',
        'numpy',
        'scipy',
        'scipy.optimize',
        'scipy.integrate',
        'scienceplots',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OTK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for GUI-only mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
