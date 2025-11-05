# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for 2-Stream RT Photon Demo
Builds a standalone executable with all dependencies bundled
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect pygame-gui theme files and data
datas = []
datas += collect_data_files('pygame_gui')

# Hidden imports that PyInstaller might miss
hiddenimports = []
hiddenimports += collect_submodules('pygame')
hiddenimports += collect_submodules('pygame_gui')
hiddenimports += ['numpy', 'numpy.core._methods', 'numpy.lib.format']
hiddenimports += ['pygame.constants', 'pygame.locals']

a = Analysis(
    ['src/photon_demo.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'PIL', 'tkinter'],  # Exclude unused large packages
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PhotonDemo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression - can cause issues with pygame
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PhotonDemo.app',
        icon=None,
        bundle_identifier='com.photon.demo',
        info_plist={
            'CFBundleName': '2-Stream RT Photon Demo',
            'CFBundleDisplayName': '2-Stream RT Photon Simulator',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
        },
    )
