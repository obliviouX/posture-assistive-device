import aioble
import bluetooth
import asyncio
import struct
from sys import exit
from display_functions import *
from pimoroni import RGBLED

devices_conn = 0 # keeps track of how long it has been without a device being connected

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

led = RGBLED(26, 27, 28)
led.set_rgb(5,5,5)
# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Central"
RECEIVING_FROM = ["Left_Wrist", "Right_Wrist", "Neck"]  # List of peripheral names

# Bluetooth parameters
BLE_NAME = f"{IAM}"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 1200
BLE_INTERVAL = 30000
BLE_WINDOW = 15000


def decode_message(message):
    return message.decode('utf-8')


async def receive_data_task(characteristic,connection):
    global devices_conn
    # for some reason, this central device would receive multiple messages/lines of data
    # so num_messages_received checks to see when 1 message is received then breaks out of the loop.
    # basically it acts like a flag for when one message is received.
    num_messages_received = 0
    
    while True:
        try:
            data = await characteristic.read()

            if data:
                num_messages_received = 1
                received_data = decode_message(data)
                #print("Raw data:")
                #print(data)
                numbers = received_data.split(',')
                #print("Device: ", numbers[0], "Roll: ", numbers[1], "Pitch: ", numbers[2], "Yaw: ", numbers[3], end="\n")
                print(numbers[0], numbers[1], numbers[3])
                update_display(numbers[1], numbers[3], numbers[0], devices_conn)  # flexion, radial, device
                if num_messages_received == 1:
                    connection.disconnect()
                    await asyncio.sleep(2)
                    break

        except asyncio.TimeoutError:
            #print("Timeout waiting for data.")
            led.set_rgb(5,0,0)
            break
        except Exception as e:
            #print(f"Error receiving data: {e}")
            led.set_rgb(5,0,0)
            break


async def ble_scan(peripheral_name):
    global BLE_SCAN_LENGTH, BLE_INTERVAL, BLE_WINDOW
    # Scan for a BLE device with the matching name and service UUID

    #print(f"Scanning for BLE Peripheral named {peripheral_name}...")

    async with aioble.scan(BLE_SCAN_LENGTH, interval_us=BLE_INTERVAL, window_us=BLE_WINDOW, active=True) as scanner:
        async for result in scanner:
            if result.name() == peripheral_name and BLE_SVC_UUID in result.services():
                #print(f"found {result.name()} with service uuid {BLE_SVC_UUID}")
                return result
    return None


async def run_central_mode():
    global devices_conn
    # Loop through each peripheral in RECEIVING_FROM
    for peripheral_name in RECEIVING_FROM:
        device = await ble_scan(peripheral_name)

        if device is None:
            #print(f"{peripheral_name} not found. Skipping.")
            devices_conn += 1
            if devices_conn > 10:
                devices_conn = 10
                update_display(0,0,4,devices_conn)
            continue
        #print(f"Device found: {device}, name is {device.name()}")
        
        devices_conn = 0
        
        try:
            #print(f"Connecting to {device.name()}")
            connection = await device.device.connect()

        except asyncio.TimeoutError:
            #print("Timeout during connection")
            led.set_rgb(5,0,0)
            continue

        #print(f"{IAM} connected to {connection}")

        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
            except (asyncio.TimeoutError, AttributeError):
                #print("Timed out discovering services/characteristics")
                led.set_rgb(5,0,0)
                continue
            except Exception as e:
                #print(f"Error discovering services {e}")
                led.set_rgb(5,0,0)
                await connection.disconnect()
                continue

            tasks = [
                asyncio.create_task(receive_data_task(characteristic,connection)),
            ]
            await asyncio.gather(*tasks)

            # Disconnect after receiving data
            await connection.disconnected()
            #print(f"{IAM} disconnected from {device.name()}")

            # Delay before connecting to the next device
            await asyncio.sleep(0.5)

async def main():
    show_connected_device(4) # show a red circle to notify nothing is connected
    display_startup()
    display.update()
    while True:
        led.set_rgb(5,5,5)
        tasks = [
            asyncio.create_task(run_central_mode()),
        ]
        await asyncio.gather(*tasks)

asyncio.run(main())

