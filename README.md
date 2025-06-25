# 🤖 LeRobot Installer

An automated GUI application that installs LeRobot with all dependencies in one click.

## What This App Does

This installer automatically handles the complete LeRobot installation process:

1. **System Check** - Verifies git and conda are installed
2. **Repository Clone** - Downloads LeRobot from GitHub (`git clone https://github.com/huggingface/lerobot.git`)
3. **Environment Setup** - Creates conda environment with Python 3.10 (`conda create -y -n lerobot python=3.10`)
4. **FFmpeg Installation** - Installs ffmpeg via conda-forge (`conda install ffmpeg -c conda-forge`)
5. **LeRobot Installation** - Installs the main package (`pip install -e .`)
6. **Dynamixel SDK** - Installs motor control SDK (`pip install -e ".[dynamixel]"`)
7. **System Dependencies** - Installs platform-specific build tools
8. **Verification** - Tests the installation

### Motor Configuration (After Installation)

The installer also includes a motor configuration tool that helps you:

- **Find USB Ports** - Automatically discovers robot arm USB connections
- **Interactive Setup** - Guides you through unplugging/reconnecting arms
- **Port Identification** - Uses `python lerobot/find_port.py` to identify ports
- **Step-by-step Process** - Clear instructions for follower and leader arm setup

## Prerequisites

Before running the installer, make sure you have:

- **Git** - Download from [git-scm.com](https://git-scm.com/)
- **Conda** - Download Miniconda from [docs.conda.io](https://docs.conda.io/en/latest/miniconda.html)
- **Python 3.6+** - Usually comes with conda

## Download & Run

### Option 1: Run Desktop Installer

**Beautiful desktop app with Tune Robotics design:**
1. Download `robot_installer.py`
2. Open terminal/command prompt  
3. Navigate to download directory
4. Run: `python robot_installer.py`

### Option 2: Create Executable (Advanced)

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable (GUI version)
pyinstaller --onefile --windowed robot_installer.py

# The executable will be in the 'dist' folder
```

## How to Use

1. **Launch the app** - Run `python robot_installer.py` or double-click the executable
2. **Review installation info** - Check the installation directory and steps
3. **Click "Start Installation"** - The app will handle everything automatically
4. **Monitor progress** - Watch the visual progress indicators and detailed log output
5. **Installation complete** - Follow the final instructions to start using LeRobot
6. **Configure Motors** - Click "Configure Motors" to set up robot hardware (if applicable)

## Installation Directory

By default, LeRobot will be installed to:
- **Windows**: `C:\Users\[username]\lerobot`
- **macOS**: `/Users/[username]/lerobot`
- **Linux**: `/home/[username]/lerobot`

**🔧 Change Directory**: Click the "Change Directory" button in the installer to choose a different installation location before starting the installation.

## After Installation

Once installation is complete:

1. Open terminal/command prompt
2. Activate the environment: `conda activate lerobot`
3. Navigate to LeRobot: `cd ~/lerobot` (or your install directory)
4. **Configure Motors** (if you have robot hardware):
   - Click "Configure Motors" in the installer
   - Follow the interactive prompts to identify USB ports
   - The app will guide you through unplugging/reconnecting arms
5. Start using LeRobot!

## Platform-Specific Notes

### Linux
The installer will attempt to install build dependencies:
```bash
sudo apt-get install cmake build-essential python3-dev pkg-config
sudo apt-get install libavformat-dev libavcodec-dev libavdevice-dev
sudo apt-get install libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
```

### macOS
If you have Homebrew installed, the app will install:
```bash
brew install cmake pkg-config
```

### Windows
Additional dependencies may need manual installation for some features.

## Troubleshooting

### "Git not found"
- Install Git from [git-scm.com](https://git-scm.com/)
- Make sure Git is in your system PATH

### "Conda not found"
- Install Miniconda from [docs.conda.io](https://docs.conda.io/en/latest/miniconda.html)
- Restart your terminal after installation

### "Permission denied"
- On Linux/macOS, you may need to run: `chmod +x robot_installer.py`
- For system dependencies, the installer may prompt for admin password

### Build Errors
If you encounter build errors, manually install:
- **Linux**: `sudo apt-get install cmake build-essential`
- **macOS**: `xcode-select --install` or install Xcode from App Store
- **Windows**: Install Visual Studio Build Tools

## Features

- ✅ **One-click installation** - No manual commands needed
- ✅ **Flexible installation directory** - Choose any location or use default ~/lerobot
- ✅ **Real-time progress** - Visual progress bar and detailed logging
- ✅ **Error handling** - Clear error messages and troubleshooting
- ✅ **Cross-platform** - Works on Windows, macOS, and Linux
- ✅ **Automatic cleanup** - Removes old installations before installing
- ✅ **Verification** - Tests installation to ensure everything works
- ✅ **Motor configuration** - Interactive USB port discovery for robot arms
- ✅ **Hardware setup** - Guides through physical robot setup steps
- ✅ **Modern design** - Beautiful Tune Robotics styled desktop interface
- ✅ **Visual feedback** - Color-coded progress indicators and status updates

## Technical Details

- **GUI Framework**: Python Tkinter with custom Tune Robotics styling
- **Dependencies**: None (pure Python with built-in libraries)
- **Design System**: Dark navy theme with Roboto Mono typography
- **Installation Location**: `~/lerobot`
- **Conda Environment**: `lerobot` with Python 3.10
- **Threading**: UI remains responsive during installation
- **Visual Features**: Color-coded status indicators and real-time progress tracking

## Contributing

To modify or improve the installer:

1. Edit `robot_installer.py`
2. Test on your platform
3. Submit pull requests for improvements

## License

This installer follows the same license as the LeRobot project.

## Support

For issues with:
- **The installer itself**: Check this README and troubleshooting section
- **LeRobot functionality**: Visit the [LeRobot repository](https://github.com/huggingface/lerobot)
- **Conda/Git installation**: Check official documentation

---

**Happy Robot Building! 🤖** 