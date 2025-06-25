# 📦 LeRobot Installer - Distribution Guide

This document explains how to package and distribute the LeRobot installer application.

## Package Contents

The LeRobot installer package contains these files:

### Core Files (Required)
- `robot_installer.py` - Main GUI installer application
- `README.md` - User documentation and instructions

### Launcher Scripts (Recommended)
- `launch_installer.py` - Cross-platform Python launcher with error checking
- `launch_installer.bat` - Windows batch file launcher

### Development Files (Optional)
- `build_executable.py` - Script to create standalone executable
- `requirements.txt` - Dependencies (empty for installer, used by main app)
- `DISTRIBUTION.md` - This file

## Distribution Options

### Option 1: Python Script Package (Simplest)

**What to distribute:**
```
lerobot-installer/
├── robot_installer.py
├── README.md
├── launch_installer.py
└── launch_installer.bat
```

**User requirements:**
- Python 3.6+ with tkinter

**How users run it:**
- Windows: Double-click `launch_installer.bat`
- Mac/Linux: Run `python3 launch_installer.py` or `./launch_installer.py`

### Option 2: Standalone Executable (Best User Experience)

**How to create:**
1. Run `python build_executable.py`
2. Find executable in `dist/` folder

**What to distribute:**
- Windows: `LeRobot_Installer.exe` + `README.md`
- Mac: `LeRobot_Installer` + `README.md`
- Linux: `LeRobot_Installer` + `README.md`

**User requirements:**
- None (fully self-contained)

**How users run it:**
- Double-click the executable file

## Packaging Instructions

### For ZIP Distribution

1. Create folder structure:
```bash
mkdir lerobot-installer-v1.0
cp robot_installer.py README.md launch_installer.* lerobot-installer-v1.0/
```

2. Create ZIP file:
```bash
zip -r lerobot-installer-v1.0.zip lerobot-installer-v1.0/
```

### For Executable Distribution

1. Build executable:
```bash
python build_executable.py
```

2. Create distribution folder:
```bash
mkdir lerobot-installer-v1.0-[platform]
cp dist/LeRobot_Installer* README.md lerobot-installer-v1.0-[platform]/
```

3. Create platform-specific packages:
```bash
# Windows
zip -r lerobot-installer-v1.0-windows.zip lerobot-installer-v1.0-windows/

# macOS  
tar -czf lerobot-installer-v1.0-macos.tar.gz lerobot-installer-v1.0-macos/

# Linux
tar -czf lerobot-installer-v1.0-linux.tar.gz lerobot-installer-v1.0-linux/
```

## File Size Estimates

- **Python scripts**: ~20KB total
- **Standalone executable**: 
  - Windows: ~15-25MB
  - Mac: ~20-30MB  
  - Linux: ~20-30MB

## Distribution Channels

### GitHub Releases
1. Create release tag (e.g., `v1.0.0`)
2. Upload ZIP/archive files
3. Include release notes

### Direct Download
- Host files on web server
- Provide direct download links
- Include checksums for verification

### Package Managers
- **Windows**: Consider creating installer with NSIS/Inno Setup
- **macOS**: Create `.dmg` disk image
- **Linux**: Create `.deb` or `.rpm` packages

## Installation Instructions for Users

Include these instructions with your distribution:

### Python Script Version
1. Extract the ZIP file
2. Open terminal/command prompt in extracted folder
3. Windows: Double-click `launch_installer.bat`
4. Mac/Linux: Run `python3 launch_installer.py`

### Executable Version
1. Extract the archive
2. Double-click the `LeRobot_Installer` executable
3. Follow the on-screen instructions

## Security Considerations

- Users may see security warnings for executables (especially on Mac/Windows)
- Consider code signing for executables to reduce warnings
- Provide checksums (SHA256) for download verification

## Version Management

Recommended version numbering: `MAJOR.MINOR.PATCH`
- Update version in `robot_installer.py` title
- Update filename in distribution packages
- Tag releases in version control

## Testing Before Distribution

1. Test on clean systems without Python
2. Test on different operating systems
3. Verify all links and dependencies work
4. Test both normal and error scenarios

## Support

For distribution issues, provide:
- Platform compatibility matrix
- Known issues and workarounds
- Contact information for support
- Link to main LeRobot documentation

---

**Ready to distribute? Choose your preferred option above and follow the packaging instructions!** 