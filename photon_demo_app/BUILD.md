# Building Standalone Executables

This guide explains how to build standalone executables for the 2-Stream RT Photon Demo app for Mac, Linux, and Windows.

## Prerequisites

- Python 3.8+
- Virtual environment with all dependencies installed
- PyInstaller (will be installed automatically by build scripts)

## Quick Start

### macOS / Linux

```bash
cd photon_demo_app
./build.sh
```

The build script will:
1. Activate the virtual environment
2. Install PyInstaller if needed
3. Clean previous builds
4. Create a standalone executable

**Output:**
- macOS: `dist/PhotonDemo.app`
- Linux: `dist/PhotonDemo`

### Windows

```cmd
cd photon_demo_app
build.bat
```

**Output:** `dist\PhotonDemo.exe`

## Distribution

### macOS

1. Compress the app bundle:
   ```bash
   cd dist
   zip -r PhotonDemo.zip PhotonDemo.app
   ```
2. Share `PhotonDemo.zip` with users
3. Users extract and double-click PhotonDemo.app to run

### Linux

1. Package the executable:
   ```bash
   cd dist
   tar -czf PhotonDemo.tar.gz PhotonDemo
   ```
2. Share the tarball with users
3. Users extract and run:
   ```bash
   ./PhotonDemo
   ```

### Windows

1. Copy the entire `dist` folder
2. Share with users
3. Users run `PhotonDemo.exe`

## File Structure

```
photon_demo_app/
├── build.sh              # macOS/Linux build script
├── build.bat             # Windows build script
├── photon_demo.spec      # PyInstaller configuration
├── src/
│   ├── photon_demo.py    # Main application
│   ├── photon_animation.py
│   └── config.py
└── dist/                 # Build output (created by build scripts)
    └── PhotonDemo[.app/.exe]
```

## Customization

### Changing the App Icon

1. Create an icon file:
   - macOS: `.icns` file (512x512 recommended)
   - Windows: `.ico` file (256x256 recommended)
   - Linux: `.png` file (512x512 recommended)

2. Edit `photon_demo.spec`:
   ```python
   icon='path/to/your/icon.icns'  # or .ico on Windows
   ```

### App Bundle Info (macOS)

Edit the `info_plist` section in `photon_demo.spec`:
```python
info_plist={
    'CFBundleName': 'Your App Name',
    'CFBundleDisplayName': 'Display Name',
    'CFBundleVersion': '1.0.0',
    ...
}
```

## Troubleshooting

### "Module not found" errors

Add missing modules to `hiddenimports` in `photon_demo.spec`:
```python
hiddenimports += ['your_missing_module']
```

### pygame-ce issues

The spec file is configured to use pygame-ce. If you have issues:
1. Ensure pygame-ce is installed (not regular pygame)
2. Check that all pygame_gui data files are collected

### Large executable size

The executable includes Python, pygame, numpy, and all dependencies (~100-200 MB). This is normal for PyInstaller builds.

### Console window appears (Windows)

To hide the console window, edit `photon_demo.spec`:
```python
console=False  # Set to True for debugging
```

## Building for Multiple Platforms

You must build on each target platform:
- Build on macOS → macOS executable
- Build on Windows → Windows executable  
- Build on Linux → Linux executable

Cross-compilation is not supported by PyInstaller.

## Development vs Release Builds

**Development** (with console for debugging):
```python
# In photon_demo.spec
console=True
debug=True
```

**Release** (no console):
```python
# In photon_demo.spec
console=False
debug=False
```
