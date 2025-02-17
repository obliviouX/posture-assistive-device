import aioble
import bluetooth
import asyncio
from sys import exit
from machine import Pin, I2C
import struct
from helpers import *
from mpu9250 import MPU9250
from utime import sleep
import time

# green LED on Pico
onboard_LED = Pin("LED", Pin.OUT)
onboard_LED.toggle()

# IMU I2C SETUP
i2c_hand = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000) # define i2c pins
i2c_arm = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)

arm_imu = MPU9250(i2c_arm)               # define the address of the arm imu
hand_imu = MPU9250(i2c_hand)             # define the address of the hand imu

arm_offset, arm_scale = arm_imu.ak8963.calibrate(count=5)
hand_offset, hand_scale = hand_imu.ak8963.calibrate(count=5)

rgb_led(0, 0, 0)
onboard_LED.toggle()

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# Change 'IAM' to 'Left_Wrist' or 'Right_Wrist'
#IAM = "Right_Wrist"
IAM = "Left_Wrist"
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
    hand_ax = hand_imu.acceleration[0]
    hand_ay = hand_imu.acceleration[1]
    hand_az = hand_imu.acceleration[2]

    hand_mx, hand_my, hand_mz = hand_imu.magnetic

    arm_ax = arm_imu.acceleration[0]
    arm_ay = arm_imu.acceleration[1]
    arm_az = arm_imu.acceleration[2]

    arm_mx, arm_my, arm_mz = arm_imu.magnetic

    roll_diff, pitch_diff, yaw_diff = calc_wrist_angles(hand_ax, hand_ay, hand_az, arm_ax, arm_ay, arm_az, hand_mx, hand_my, hand_mz, arm_mx, arm_my, arm_mz)
    
    # Data structure: message = f"device,roll,pitch,yaw"
    # device: 1 = Left_Wrist
    # device: 2 = Right_Wrist
    # device: 3 = Neck
    # for the Neck, put a character that will never be used in the pitch and yaw so
    # the Central sees it and skips over them
    message = f"1,{roll_diff},{pitch_diff},{yaw_diff}"
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
            print("Sleeping for 5 seconds.\n")
            await asyncio.sleep(2)
            
    #print(f"{IAM} disconnected, waiting before advertising again...")
    #print("Entering sleep for 5 seconds...\n")  # Explicit new line
    #await asyncio.sleep(5)  # Pause for 5 seconds before advertising again
    #time.sleep(5)				# sleep for 5 seconds
    #asyncio.sleep(5)			# async sleep for 5 seconds
    #machine.lightsleep(5000)  	# light sleep for 5 seconds
    #machine.deepsleep(5000)	# deep sleep for 5 seconds (also may need to disable wifi chip)

async def main():
    #UNCOMMENT BELOW TO USE BLE, COMMENTED OUT FOR TESTING DATA STORAGE
    #while True:
        
        # Create a BLE task to run asynchronously
        #tasks = [
        #    asyncio.create_task(run_peripheral_mode()), # Run the run_peripheral_mode() function asynchronously
        #]
        #await asyncio.gather(*tasks)

    #COMMENT THIS OUT IF NOT TESTING CALIBRATION OR DATA STORAGE
    print("ARM OFFSET: ", arm_offset[1], " ARM SCALE: ", arm_scale[1])
    print("HAND OFFSET: ", hand_offset, " HAND SCALE: ", hand_scale)

asyncio.run(main())
