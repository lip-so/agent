#!/usr/bin/env python3
"""
Robot Setup Server
Automated server for setting up LeRobot with minimal user interaction
"""

import os
import sys
import subprocess
import json
import time
import threading
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class RobotSetupManager:
    def __init__(self):
        self.setup_status = {
            'installation': {'status': 'pending', 'progress': 0, 'message': ''},
            'port_discovery': {'status': 'pending', 'progress': 0, 'message': '', 'ports': []},
            'motor_config': {'status': 'pending', 'progress': 0, 'message': ''},
            'calibration': {'status': 'pending', 'progress': 0, 'message': ''},
            'complete': False
        }
        self.discovered_ports = []
        self.robot_config = {}
        
    def run_command(self, command, cwd=None, timeout=300):
        """Run shell command and return output"""
        try:
            logger.info(f"Running command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def install_lerobot(self):
        """Install LeRobot and dependencies"""
        try:
            self.setup_status['installation']['status'] = 'running'
            self.setup_status['installation']['message'] = 'Installing LeRobot...'
            self.setup_status['installation']['progress'] = 10
            
            # Check if we're in the lerobot directory
            lerobot_path = Path('./lerobot')
            if not lerobot_path.exists():
                self.setup_status['installation']['message'] = 'LeRobot directory not found'
                self.setup_status['installation']['status'] = 'error'
                return False
            
            # Install in development mode
            self.setup_status['installation']['progress'] = 30
            self.setup_status['installation']['message'] = 'Installing LeRobot in development mode...'
            
            result = self.run_command('pip install -e .', cwd='./lerobot')
            if not result['success']:
                self.setup_status['installation']['message'] = f'Failed to install LeRobot: {result["stderr"]}'
                self.setup_status['installation']['status'] = 'error'
                return False
            
            # Install Dynamixel SDK
            self.setup_status['installation']['progress'] = 60
            self.setup_status['installation']['message'] = 'Installing Dynamixel SDK...'
            
            result = self.run_command('pip install -e ".[dynamixel]"', cwd='./lerobot')
            if not result['success']:
                self.setup_status['installation']['message'] = f'Failed to install Dynamixel SDK: {result["stderr"]}'
                self.setup_status['installation']['status'] = 'error'
                return False
            
            # Install additional dependencies
            self.setup_status['installation']['progress'] = 80
            self.setup_status['installation']['message'] = 'Installing additional dependencies...'
            
            deps = ['pyserial', 'opencv-python', 'numpy']
            for dep in deps:
                result = self.run_command(f'pip install {dep}')
                if not result['success']:
                    logger.warning(f'Failed to install {dep}: {result["stderr"]}')
            
            self.setup_status['installation']['progress'] = 100
            self.setup_status['installation']['message'] = 'LeRobot installation completed'
            self.setup_status['installation']['status'] = 'completed'
            return True
            
        except Exception as e:
            self.setup_status['installation']['message'] = f'Installation error: {str(e)}'
            self.setup_status['installation']['status'] = 'error'
            return False
    
    def discover_ports(self):
        """Discover USB ports for robot motors"""
        try:
            self.setup_status['port_discovery']['status'] = 'running'
            self.setup_status['port_discovery']['message'] = 'Discovering USB ports...'
            self.setup_status['port_discovery']['progress'] = 20
            
            # Run the port discovery script
            result = self.run_command('python lerobot/find_port.py', cwd='./lerobot')
            
            if result['success']:
                # Parse the output to extract ports
                output_lines = result['stdout'].split('\n')
                ports = []
                for line in output_lines:
                    if '/dev/' in line or 'COM' in line:
                        # Extract port names
                        import re
                        port_matches = re.findall(r'(/dev/[^\s,\]]+|COM\d+)', line)
                        ports.extend(port_matches)
                
                self.discovered_ports = list(set(ports))  # Remove duplicates
                self.setup_status['port_discovery']['ports'] = self.discovered_ports
                self.setup_status['port_discovery']['progress'] = 100
                self.setup_status['port_discovery']['message'] = f'Found {len(self.discovered_ports)} ports'
                self.setup_status['port_discovery']['status'] = 'completed'
                return True
            else:
                self.setup_status['port_discovery']['message'] = f'Port discovery failed: {result["stderr"]}'
                self.setup_status['port_discovery']['status'] = 'error'
                return False
                
        except Exception as e:
            self.setup_status['port_discovery']['message'] = f'Port discovery error: {str(e)}'
            self.setup_status['port_discovery']['status'] = 'error'
            return False
    
    def setup_motors(self, robot_type, port, robot_id):
        """Setup motors for the specified robot"""
        try:
            self.setup_status['motor_config']['status'] = 'running'
            self.setup_status['motor_config']['message'] = f'Configuring {robot_type} motors...'
            self.setup_status['motor_config']['progress'] = 20
            
            if robot_type == 'follower':
                cmd = f'python -m lerobot.setup_motors --robot.type=koch_follower --robot.port={port}'
            elif robot_type == 'leader':
                cmd = f'python -m lerobot.setup_motors --teleop.type=koch_leader --teleop.port={port}'
            else:
                raise ValueError(f'Unknown robot type: {robot_type}')
            
            # Note: This would normally require interactive input
            # In a real implementation, you'd need to handle the interactive prompts
            self.setup_status['motor_config']['message'] = 'Motor setup requires manual intervention - see terminal'
            self.setup_status['motor_config']['progress'] = 50
            
            result = self.run_command(cmd, cwd='./lerobot', timeout=600)
            
            if result['success']:
                self.setup_status['motor_config']['progress'] = 100
                self.setup_status['motor_config']['message'] = f'{robot_type.capitalize()} motors configured successfully'
                self.setup_status['motor_config']['status'] = 'completed'
                return True
            else:
                self.setup_status['motor_config']['message'] = f'Motor setup failed: {result["stderr"]}'
                self.setup_status['motor_config']['status'] = 'error'
                return False
                
        except Exception as e:
            self.setup_status['motor_config']['message'] = f'Motor setup error: {str(e)}'
            self.setup_status['motor_config']['status'] = 'error'
            return False
    
    def calibrate_robot(self, robot_type, port, robot_id):
        """Calibrate the robot"""
        try:
            self.setup_status['calibration']['status'] = 'running'
            self.setup_status['calibration']['message'] = f'Calibrating {robot_type}...'
            self.setup_status['calibration']['progress'] = 20
            
            if robot_type == 'follower':
                cmd = f'python -m lerobot.calibrate --robot.type=koch_follower --robot.port={port} --robot.id={robot_id}'
            elif robot_type == 'leader':
                cmd = f'python -m lerobot.calibrate --teleop.type=koch_leader --teleop.port={port} --teleop.id={robot_id}'
            else:
                raise ValueError(f'Unknown robot type: {robot_type}')
            
            self.setup_status['calibration']['message'] = 'Calibration requires manual intervention - see terminal'
            self.setup_status['calibration']['progress'] = 50
            
            result = self.run_command(cmd, cwd='./lerobot', timeout=600)
            
            if result['success']:
                self.setup_status['calibration']['progress'] = 100
                self.setup_status['calibration']['message'] = f'{robot_type.capitalize()} calibrated successfully'
                self.setup_status['calibration']['status'] = 'completed'
                return True
            else:
                self.setup_status['calibration']['message'] = f'Calibration failed: {result["stderr"]}'
                self.setup_status['calibration']['status'] = 'error'
                return False
                
        except Exception as e:
            self.setup_status['calibration']['message'] = f'Calibration error: {str(e)}'
            self.setup_status['calibration']['status'] = 'error'
            return False

# Global setup manager
setup_manager = RobotSetupManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(setup_manager.setup_status)

@app.route('/api/install', methods=['POST'])
def install():
    def run_installation():
        setup_manager.install_lerobot()
    
    thread = threading.Thread(target=run_installation)
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/discover_ports', methods=['POST'])
def discover_ports():
    def run_discovery():
        setup_manager.discover_ports()
    
    thread = threading.Thread(target=run_discovery)
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/setup_motors', methods=['POST'])
def setup_motors():
    data = request.json
    robot_type = data.get('robot_type')
    port = data.get('port')
    robot_id = data.get('robot_id', f'{robot_type}_arm')
    
    def run_motor_setup():
        setup_manager.setup_motors(robot_type, port, robot_id)
    
    thread = threading.Thread(target=run_motor_setup)
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/calibrate', methods=['POST'])
def calibrate():
    data = request.json
    robot_type = data.get('robot_type')
    port = data.get('port')
    robot_id = data.get('robot_id', f'{robot_type}_arm')
    
    def run_calibration():
        setup_manager.calibrate_robot(robot_type, port, robot_id)
    
    thread = threading.Thread(target=run_calibration)
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/api/save_config', methods=['POST'])
def save_config():
    data = request.json
    config_file = 'robot_config.json'
    
    try:
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'status': 'success', 'message': 'Configuration saved'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("Starting Robot Setup Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True) 