import serial
import csv
import os
import serial.tools.list_ports
import sys
from datetime import datetime

# Function to detect available serial ports
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return ports

# Function to automatically detect Pico (basic, can be improved)
def find_pico_port():
    ports = list_serial_ports()
    for port in ports:
        if "USB" in port.description or "Board" in port.description:
            return port.device
    return None

# Function to check if the serial port works
def check_serial_port(serial_port, baud_rate=115200):
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1):
            return True
    except serial.SerialException:
        return False

# Ask user to choose detection mode
print("Choose an option:")
print("1. Automatically detect the device.")
print("2. Choose a port from the list.")

user_choice = input("Enter 1 or 2: ").strip()

if user_choice == "1":
    # Try to auto-detect the Pico
    serial_port = find_pico_port()

    if not serial_port:
        print("Posture Assistive Device not found.")
        sys.exit(1)

    print(f"Automatically detected: {serial_port}")

elif user_choice == "2":
    available_ports = list_serial_ports()

    if not available_ports:
        print("No serial ports detected. Please check your connection.")
        sys.exit(1)

    print("\nAvailable serial ports:")
    for i, port in enumerate(available_ports):
        print(f"[{i}] {port.device} - {port.description}")

    # Ask the user to input the port number
    while True:
        try:
            index = int(input("Enter the number of the port to use: "))
            if index < 0 or index >= len(available_ports):
                print("Invalid number. Please choose a valid port number.")
            else:
                serial_port = available_ports[index].device
                break
        except ValueError:
            print("Please enter a valid number.")

    print(f"Selected port: {serial_port}")

else:
    print("Invalid choice. Exiting.")
    sys.exit(1)

# Validate the selected port
while not check_serial_port(serial_port):
    print(f"Could not open port {serial_port}. Please check if the port is correct.")
    serial_port = input("Enter a valid COM port manually (e.g., COM3 or /dev/ttyACM0): ")

baud_rate = 115200
file_name = "data.csv"

# Define column headers
headers = ["Timestamp", "Left_Wrist_Radial", "Left_Wrist_Flexion", "Right_Wrist_Radial", "Right_Wrist_Flexion", "Back_Angle"]

# Check if file exists
file_exists = os.path.exists(file_name)

with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_name, "a", newline="") as file:
    writer = csv.writer(file)

    # Write header if file is new
    if not file_exists:
        writer.writerow(headers)
        file.flush()

    print(f"Using device on {serial_port}.")
    print(f"Logging data...")
    print(f"Press 'Ctrl+C' at any time to stop.")

    latest_values = {"1": ["", ""], "2": ["", ""], "3": [""]}

    
    try:
        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                parts = line.split(",")
                if len(parts) >= 2:
                    sensor_id = parts[0]
                    values = parts[1:]
                    latest_values[sensor_id] = values

                row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                row.extend(latest_values["1"])
                row.extend(latest_values["2"])
                row.extend(latest_values["3"])

                writer.writerow(row)
                file.flush()
                print(row)

    except KeyboardInterrupt:
        print("Data collection stopped.")

    finally:
        try:
            ser.close()
        except:
            pass
        print("Cleanup complete.")
