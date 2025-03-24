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
import ujson as json

orange_led()

# turn off green LED on Pico
onboard_LED = Pin("LED", Pin.OUT)
onboard_LED.off()

# setup calibration button
c_button = Pin(10, Pin.IN, Pin.PULL_UP)
c_state = button.value()

# set up imu power pins
arm_imu_power = Pin(21, Pin.OUT)
arm_imu_power.on()

wrist_imu_power = Pin(20, Pin.OUT)
wrist_imu_power.on()

# imu i2c setup
i2c_hand = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000) # define i2c pins
i2c_arm = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)


time.sleep(1)

#hand_imu = MPU9250(i2c_hand)             # define the address of the hand imu
#arm_imu = MPU9250(i2c_arm)               # define the address of the arm imu
#e
# calibration setup
# checks if button is being held down on startup to initiate calibration
if c_state == True:
    hand_offset, hand_scale = hand_imu.ak8963.calibrate(count=100)
    arm_offset, arm_scale = arm_imu.ak8963.calibrate(count=100)
    
    jsonData = {"hand_offset_x": hand_offset[1], "hand_offset_y": hand_offset[2], "hand_offset_z": hand_offset[3],
                "hand_scale_x": hand_scale[1], "hand_scale_y": hand_scale[2], "hand_scale_z": hand_scale[3],
                "arm_offset_x": arm_offset[1], "arm_offset_y": arm_offset[2], "arm_offset_z": arm_offset[3],
                "arm_scale_x": arm_scale[1], "arm_scale_y": arm_scale[2], "arm_scale_z": arm_scale[3]
                }
    try:
        with open('savedata.json', 'w') as f:
            json.dump(jsonData, f)
    except:
        red_led()

    # After calibration, update the IMU with the new offsets and scales
    ak8963_hand = AK8963(hand_imu, offset=(hand_offset[1], hand_offset[2], hand_offset[3]),
                         scale=(hand_scale[1], hand_scale[2], hand_scale[3]))
    ak8963_arm = AK8963(arm_imu, offset=(arm_offset[1], arm_offset[2], arm_offset[3]),
                        scale=(arm_scale[1], arm_scale[2], arm_scale[3]))

    hand_imu = MPU9250(i2c_hand, ak8963=ak8963_hand)
    arm_imu = MPU9250(i2c_arm, ak8963=ak8963_arm)

else:
    try:
        with open('savedata.json', 'r') as f:
            data = json.load(f)
            hand_offset_x = data["hand_offset_x"]
            hand_offset_y = data["hand_offset_y"]
            hand_offset_z = data["hand_offset_z"]
            hand_scale_x = data["hand_scale_x"]
            hand_scale_y = data["hand_scale_y"]
            hand_scale_z = data["hand_scale_z"]

            arm_offset_x = data["arm_offset_x"]
            arm_offset_y = data["arm_offset_y"]
            arm_offset_z = data["arm_offset_z"]
            arm_scale_x = data["arm_scale_x"]
            arm_scale_y = data["arm_scale_y"]
            arm_scale_z = data["arm_scale_z"]

        dummy_hand = MPU9250(i2c_hand)  # dummy to open up access to the ak8963
        dummy_arm = MPU9250(i2c_arm)

        ak8963_hand = AK8963(hand_imu, offset=(hand_offset_x, hand_offset_y, hand_offset_z), scale=(hand_scale_x, hand_scale_y, hand_scale_z))
        ak8963_arm = AK8963(arm_imu, offset=(arm_offset_x, arm_offset_y, arm_offset_z), scale=(arm_scale_x, arm_scale_y, arm_scale_z))
        
        hand_imu = MPU9250(i2c_hand,ak9863=ak8963_hand)
        arm_imu = MPU9250(i2c_arm, ak9863=ak8963_arm)
    except:
        red_led()


# MAIN PROGRAM

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
#IAM = "Left_Wrist"
IAM = "Left_Wrist"
IAM_SENDING_TO = "Central"

# Bluetooth parameters
BLE_NAME = f"{IAM}"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A) # central peripheral looks for this uuid
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
    message = f"2,{roll_diff},{pitch_diff},{yaw_diff}"

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
        rgb_led(0, 20000, 0)
        time.sleep(1) # can remove this, this is just to show the LED turns green when data is sent
        characteristic.write(msg)
        rgb_led(0, 0, 20000)
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

    # start to advertise BLE
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
            await asyncio.sleep(2)	# change this to 5 seconds
            
    #print(f"{IAM} disconnected, waiting before advertising again...")
    #print("Entering sleep for 5 seconds...\n")  # Explicit new line
    #await asyncio.sleep(5)  # Pause for 5 seconds before advertising again
    #time.sleep(5)				# sleep for 5 seconds
    #asyncio.sleep(5)			# async sleep for 5 seconds
    #machine.lightsleep(5000)  	# light sleep for 5 seconds
    #machine.deepsleep(5000)	# deep sleep for 5 seconds (also may need to disable wifi chip)


async def main():
    rgb_led(0, 0, 20000)
    while True:
        # create a BLE task to run asynchronously
        #UNCOMMENT BELOW THIS, COMMENTED OUT FOR TESTING
        tasks = [
            asyncio.create_task(run_peripheral_mode()), # run the run_peripheral_mode() function asynchronously
        ]
        await asyncio.gather(*tasks)

asyncio.run(main())
