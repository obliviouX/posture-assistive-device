import serial
import csv
import os
import serial.tools.list_ports
from datetime import datetime

# Function to automatically detect the connected Pico's serial port
def find_pico_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "ACM" in port.description:  # Search for "USB" or "ACM"
            return port.device
    return None

# Function to check if the user-inputted serial port works
def check_serial_port(serial_port, baud_rate=115200):
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            return True
    except serial.SerialException:
        return False

# Automatically find the connected Pico's serial port
serial_port = find_pico_port()
if not serial_port:
    print("Raspberry Pi Pico not found.")
    serial_port = input("Please enter the COM port manually (e.g., COM3 or /dev/ttyACM0): ")

    # Validate the entered port
    while not check_serial_port(serial_port):
        print(f"Could not open port {serial_port}. Please check if the port is correct and try again.")
        serial_port = input("Please enter the COM port manually (e.g., COM3 or /dev/ttyACM0): ")

baud_rate = 115200
file_name = "data.csv"

# Define column headers
headers = ["Timestamp", "Left_Wrist_Radial", "Left_Wrist_Flexion", "Right_Wrist_Radial", "Right_Wrist_Flexion", "Back_Angle"]

# Check if file exists before opening
file_exists = os.path.exists(file_name)

with serial.Serial(serial_port, baud_rate, timeout=1) as ser, open(file_name, "a", newline="") as file:
    writer = csv.writer(file)

    # Write header only if the file is newly created
    if not file_exists:
        writer.writerow(headers)
        file.flush()

    print(f"Using Pico on {serial_port}. Logging data... Press Ctrl+C to stop.")

    # Store latest values in a dictionary
    latest_values = {"1": ["", ""], "2": ["", ""], "3": [""]}

    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if line:
                parts = line.split(",")  # Expecting "sensor_id,value1,value2"
                
                if len(parts) >= 2:
                    sensor_id = parts[0]  # 1 = Left Wrist, 2 = Right Wrist, 3 = Back
                    values = parts[1:]  # The actual sensor values
                    
                    # Update latest values
                    latest_values[sensor_id] = values

                # Prepare a row with the latest known values
                row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                row.extend(latest_values["1"])  # Left wrist (radial, flexion)
                row.extend(latest_values["2"])  # Right wrist (radial, flexion)
                row.extend(latest_values["3"])  # Back (angle)

                writer.writerow(row)
                file.flush()  # Ensure real-time updates
                print(row)  # Optional: Show real-time logging output

        except KeyboardInterrupt:
            print("Data collection stopped.")
            break
