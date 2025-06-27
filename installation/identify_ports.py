#!/usr/bin/env python3
import subprocess
import os
import sys
import time

_SCRIPT_FILE = os.path.abspath(__file__)
_LEROBOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_SCRIPT_FILE)))
LEROBOT_SCRIPT_PATH = os.path.join(_LEROBOT_DIR, "find_port.py")

def clear_screen():
    """Clears the console screen for better readability."""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_single_port(device_name: str) -> str | None:

    title = f"Let's identify the {device_name.upper()} port"
    print("+" + "-" * (len(title) + 2) + "+")
    print(f"| {title} |")
    print("+" + "-" * (len(title) + 2) + "+")
    print("\nStarting the port detection tool...")

    try:
        process = subprocess.Popen(
            [sys.executable, LEROBOT_SCRIPT_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    except FileNotFoundError:
        print(f"\n[ERROR] The script '{LEROBOT_SCRIPT_PATH}' was not found.")
        print("Please make sure you are running this program from the correct directory.")
        return None
    except Exception as e:
        print(f"\n[ERROR] Failed to start the script: {e}")
        return None

    print("\n" + "="*50)
    print(">>> ACTION REQUIRED <<<")
    print(f"Please UNPLUG the USB cable from the '{device_name}' robot.")
    print("After unplugging the cable, press the ENTER key here to continue.")
    print("="*50)
    
    # This acts like a button. The program waits here until the user presses Enter.
    input() 

    # By sending a newline character to the script's standard input,
    # we simulate the user pressing "Enter" in the terminal running that script.
    # We then use communicate() to get all output and wait for it to finish.
    try:
        stdout, stderr = process.communicate(input='\n', timeout=15)
    except subprocess.TimeoutExpired:
        print("\n[ERROR] The port detection script timed out.")
        process.kill()
        return None

    if process.returncode != 0:
        print(f"\n[ERROR] The port detection script failed.")
        if stderr:
            print("Error details:")
            print(stderr.strip())
        return None

    # The port name is the output from the script's stdout.
    port_name = stdout.strip()

    if not port_name:
        print("\n[WARNING] The script did not identify a port. Please check the robot connection.")
        return None

    print(f"Success! The detected '{device_name}' port is: {port_name}")
    print("   Please remember this port name.")
    time.sleep(2) # Pause briefly so the user can read the message.
    return port_name


def main():
    """
    Main function to run the complete port identification workflow.
    """
    clear_screen()
    print("Welcome to the Robot Port Identification Helper!")
    print("This program will guide you to find the correct USB ports for your robots.")
    print("-" * 60)
    
    # First, check if the required script exists to avoid user confusion.
    if not os.path.exists(LEROBOT_SCRIPT_PATH):
        print(f"[FATAL ERROR] The necessary script was not found at: '{LEROBOT_SCRIPT_PATH}'")
        print("Please ensure the 'lerobot' directory and its 'find_port.py' script exist.")
        sys.exit(1)

    follower_port = find_single_port("follower")
    
    input("Press ENTER to proceed to the next step...")
    clear_screen()

    leader_port = find_single_port("leader")

    clear_screen()
    print("Identification Process Complete!")
    print("\nHere is a summary of the identified ports:\n")

    print(f"  Follower Port: {follower_port if follower_port else '--- NOT IDENTIFIED ---'}")
    print(f"  Leader Port:   {leader_port if leader_port else '--- NOT IDENTIFIED ---'}")

    if follower_port and leader_port:
        print("\nBoth ports were successfully identified.")
        print("You can now use these values in your robot's configuration files.")
    else:
        print("One or more ports could not be identified.")
        print("Please run the script again and follow the instructions carefully.")


if __name__ == "__main__":
    main() 