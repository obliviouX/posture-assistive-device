import aioble
import bluetooth
import asyncio
from sys import exit
from machine import Pin, I2C
import struct
from mpu9250 import MPU9250
import utime
import time
import math

# green LED on Pico
onboard_LED = Pin("LED", Pin.OUT)
onboard_LED.off()

# pin that supplies power to the IMU
imu_power = Pin(18, Pin.OUT)
imu_power.on()


# IMU I2C SETUP
i2c_neck = I2C(0,scl=Pin(17),sda=Pin(16))  # define i2c pins
neck_imu = MPU9250(i2c_neck)               # define the address of the arm imu

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Change 'IAM' to 'Left_Wrist' or 'Right_Wrist'
IAM = "Neck"
IAM_SENDING_TO = "Central"

# Bluetooth parameters
BLE_NAME = f"{IAM}"  					# You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A) 	# Central looks for this uuid
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000


def encode_message(message):
    return message.encode('utf-8')


async def get_imu_data():
    neck_ay = round(neck_imu.acceleration[1])
    neck_az = round(neck_imu.acceleration[2])
    neck_roll = math.atan2(neck_az, neck_ay) * 180 / math.pi
    neck_roll = abs(round(neck_roll))
    print(f"{neck_roll}")
    # Data structure: message = f"device,roll,pitch,yaw"
    # device: 1 = Left_Wrist
    # device: 2 = Right_Wrist
    # device: 3 = Neck
    # for the Neck, put a character that will never be used in the pitch and yaw so
    # the Central sees it and can skip over them
    pitch_diff = ''
    yaw_diff = ''
    message = f"3,{neck_roll},{pitch_diff},{yaw_diff}"
    return message


async def send_data_task(connection, characteristic):

    if not connection:
        print("error - no connection in send data")
        return

    if not characteristic:
        print("error no characteristic provided in send data")
        return

    message = await get_imu_data()
    print(f"sending message: {message}")

    try:
        msg = encode_message(message)
        characteristic.write(msg)
        await asyncio.sleep(0.5)

    except Exception as e:
        print(f"writing error {e}")


async def run_peripheral_mode():

    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(BLE_SVC_UUID)
    characteristic = aioble.Characteristic(
        ble_service,
        BLE_CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    aioble.register_services(ble_service)

    # Start to advertise BLE
    print(f"{BLE_NAME} starting to advertise", end="\n")

    while True:
        async with await aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE) as connection:
            print(f"{BLE_NAME} connected to another device: {connection.device}")

            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)
            connection.disconnect()
            print("Disconnected from the central device.")
            print("Sleeping for 4 seconds.\n")
            machine.lightsleep(4000)


async def main():
    while True:
        # Create a BLE task to run asynchronously
        tasks = [
            asyncio.create_task(run_peripheral_mode()), # Run the run_peripheral_mode() function asynchronously
        ]
        await asyncio.gather(*tasks)


asyncio.run(main())
