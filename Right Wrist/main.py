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
c_button = Pin(15, Pin.IN)
c_state = button_pin.value()

# set up imu power pins
arm_imu_power = Pin(21, Pin.OUT)
arm_imu_power.on()

wrist_imu_power = Pin(20, Pin.OUT)
wrist_imu_power.on()

# imu i2c setup
i2c_hand = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000) # define i2c pins
i2c_arm = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)

time.sleep(1)

arm_imu = MPU9250(i2c_arm)               # define the address of the arm imu
hand_imu = MPU9250(i2c_hand)             # define the address of the hand imu

time.sleep(2)
rgb_led(30000, 30000, 0)
time.sleep(2)

# calibration setup
# checks if button is being held down on startup to initiate calibration
if c_state == True:
    arm_imu.ak8963.calibrate(count=100)
    hand_imu.ak8963.calibrate(count=100)
else:
    try:
        with open('savedata.json', 'r') as f:
            data = json.load(f)
            y = data["num"]
            print(y)
    except:
        red_led()




# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
#IAM = "Left_Wrist"
IAM = "Right_Wrist"
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
