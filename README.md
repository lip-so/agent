# 🤖 LeRobot Setup Agent

An automated setup assistant for LeRobot installations with minimal user interaction. This tool provides a web-based interface to guide users through the complete LeRobot setup process including installation, port discovery, motor configuration, and calibration.

## Features

- 🌐 **Web-based Interface**: Modern, intuitive web UI for easy interaction
- 🔄 **Automated Installation**: Automatically installs LeRobot and dependencies
- 🔍 **Port Discovery**: Finds and lists available USB ports for robot connections
- ⚙️ **Motor Configuration**: Guides through motor setup for both leader and follower arms
- 📏 **Robot Calibration**: Assists with robot calibration process
- 📊 **Real-time Progress**: Live status updates and progress tracking
- 💾 **Configuration Saving**: Saves robot configurations for future use

## Prerequisites

- Python 3.8 or higher
- USB ports for robot connections
- LeRobot-compatible hardware (Koch arms, etc.)

## Quick Start

### Option 1: Automated Installation (Recommended)

1. Clone or download this repository
2. Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

3. Open your browser to `http://localhost:5000`
4. Follow the web interface to complete your robot setup

### Option 2: Manual Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python robot_setup_server.py
```

4. Open `http://localhost:5000` in your browser

## Usage Guide

### Step 1: Install LeRobot
- Click "Start Installation" to automatically install LeRobot and Dynamixel SDK
- Progress will be shown in real-time
- Installation typically takes 2-5 minutes depending on your internet connection

### Step 2: Discover USB Ports
- Connect your robot's USB cables
- Click "Discover Ports" to scan for available ports
- The system will list all detected USB ports

### Step 3: Configure Motors
- Select whether you're setting up a "Leader" or "Follower" arm
- Choose the appropriate USB port from the discovered list
- Enter a unique robot ID (e.g., "my_awesome_follower_arm")
- Click "Setup Motors" to begin motor configuration

**Note**: Motor setup requires manual intervention. You'll need to connect motors one by one as prompted in the terminal output.

### Step 4: Calibrate Robot
- After motor configuration, click "Start Calibration"
- Follow the on-screen instructions to move the robot through its calibration sequence
- This ensures accurate position mapping between leader and follower arms

## Configuration Files

The system creates the following configuration files:

- `robot_config.json`: Stores your robot configuration settings
- Various LeRobot configuration files in the `lerobot/` directory

## Troubleshooting

### Common Issues

**Port Discovery Fails**
- Ensure USB cables are properly connected
- Check that your system recognizes the USB devices
- Try unplugging and reconnecting USB cables

**Motor Setup Hangs**
- Follow the terminal prompts carefully
- Ensure only one motor is connected at a time during setup
- Check power connections to the robot

**Installation Fails**
- Ensure you have Python 3.8 or higher
- Check your internet connection
- Try running with administrator/sudo privileges if needed

### Getting Help

If you encounter issues:

1. Check the terminal output for detailed error messages
2. Ensure all hardware connections are secure
3. Verify that your robot hardware is compatible with LeRobot
4. Check the [LeRobot documentation](https://huggingface.co/docs/lerobot) for hardware-specific guidance

## Technical Details

### Architecture

- **Backend**: Flask web server with REST API
- **Frontend**: Modern HTML/CSS/JavaScript interface with real-time updates
- **Process Management**: Threaded execution for non-blocking operations
- **Status Tracking**: Real-time progress monitoring and error handling

### API Endpoints

- `GET /api/status`: Get current setup status
- `POST /api/install`: Start LeRobot installation
- `POST /api/discover_ports`: Discover USB ports
- `POST /api/setup_motors`: Configure robot motors
- `POST /api/calibrate`: Start robot calibration
- `POST /api/save_config`: Save robot configuration

### File Structure

```
agent/
├── robot_setup_server.py      # Main Flask application
├── templates/
│   └── index.html            # Web interface
├── requirements.txt          # Python dependencies
├── install.sh               # Automated installer
├── README.md               # This file
├── lerobot/               # LeRobot submodule
└── venv/                 # Virtual environment (created during install)
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project follows the same license as the included LeRobot submodule (Apache 2.0).

## Acknowledgments

- Built on top of [🤗 LeRobot](https://github.com/huggingface/lerobot)
- Designed for ease of use with robotic hardware setup
- Inspired by the need for simplified robotics onboarding 