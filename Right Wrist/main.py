import aioble
import bluetooth
import asyncio
from sys import exit
from machine import Pin, I2C, ADC
import struct
from helpers import *
from mpu9250 import MPU9250
from ak8963 import AK8963
from utime import sleep
import time
import ujson as json

for x in range(0,8):   # startup led
    if x%2 == 0:
        blue_green_led()
    else:
        led_off()
    time.sleep(0.3)
led_off()

# turn off green LED on Pico
onboard_LED = Pin("LED", Pin.OUT)
onboard_LED.off()

# setup calibration button
c_button = Pin(10, Pin.IN, Pin.PULL_UP)
c_state = c_button.value()
print(c_state)

# set up imu power pins
arm_imu_power = Pin(21, Pin.OUT)
arm_imu_power.on()

wrist_imu_power = Pin(20, Pin.OUT)
wrist_imu_power.on()

time.sleep(1)

# imu i2c setup
i2c_hand = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000) # define i2c pins
i2c_arm = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)

time.sleep(1)

#e
# calibration setup
# checks if button is being held down on startup to initiate calibration
if c_state == 0:
    hand_dummy = MPU9250(i2c_hand)
    arm_dummy = MPU9250(i2c_arm)
    ak8963_hand = AK8963(i2c_hand)
    ak8963_arm = AK8963(i2c_arm)
    
    hand_offset, hand_scale = ak8963_hand.calibrate(count=256,delay=200)
    arm_offset, arm_scale = ak8963_arm.calibrate(count=256,delay=200)
    
    jsonData = {"hand_offset_x": hand_offset[0], "hand_offset_y": hand_offset[1], "hand_offset_z": hand_offset[2],
                "hand_scale_x": hand_scale[0], "hand_scale_y": hand_scale[1], "hand_scale_z": hand_scale[2],
                "arm_offset_x": arm_offset[0], "arm_offset_y": arm_offset[1], "arm_offset_z": arm_offset[2],
                "arm_scale_x": arm_scale[0], "arm_scale_y": arm_scale[1], "arm_scale_z": arm_scale[2]
                }
    try:
        with open('savedata.json', 'w') as f:
            json.dump(jsonData, f)
    except:
        red_led()

    # After calibration, update the IMU with the new offsets and scales
    ak8963_hand = AK8963(i2c_hand, offset=(hand_offset[0], hand_offset[1], hand_offset[2]),
                         scale=(hand_scale[0], hand_scale[1], hand_scale[2]))
    ak8963_arm = AK8963(i2c_arm, offset=(arm_offset[0], arm_offset[1], arm_offset[2]),
                        scale=(arm_scale[0], arm_scale[1], arm_scale[2]))
    time.sleep(0.5)
    hand_imu = MPU9250(i2c_hand, ak8963=ak8963_hand)
    arm_imu = MPU9250(i2c_arm, ak8963=ak8963_arm)
    

else:
    try:
        with open('savedata.json', 'r') as f:
            print("OPENING SAVEDATA")
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
            
            print("OPENED SAVEDATA")
            hand_dummy = MPU9250(i2c_hand)  # dummy to open up access to the ak8963
            arm_dummy = MPU9250(i2c_arm)

            print("DUMMY IMUs CREATED")
            ak8963_hand = AK8963(i2c_hand, offset=(hand_offset_x, hand_offset_y, hand_offset_z), scale=(hand_scale_x, hand_scale_y, hand_scale_z))
            ak8963_arm = AK8963(i2c_arm, offset=(arm_offset_x, arm_offset_y, arm_offset_z), scale=(arm_scale_x, arm_scale_y, arm_scale_z))
        
            print("SETTING UP REAL IMUs")
            hand_imu = MPU9250(i2c_hand,ak8963=ak8963_hand)
            arm_imu = MPU9250(i2c_arm, ak8963=ak8963_arm)
            print("IMUs ARE SET UP")
        
    except Exception as e:
        print(f"Error in savedata: {e}")
        rgb_led(40000,40000,40000)
        time.sleep(1)
        

user_radial_offset = 0
user_flexion_offset = 0
set_offset_flag = 0

def calc_wrist_angles():
    global user_radial_offset, user_flexion_offset
    global filtered_hand_mx, filtered_hand_my, filtered_arm_mx, filtered_arm_my
    # roll (flexion/extension), yaw (radial)
    
    hand_ax = hand_imu.acceleration[0]
    hand_ay = hand_imu.acceleration[1]
    hand_az = hand_imu.acceleration[2]

    hand_mx, hand_my, hand_mz = hand_imu.magnetic

    arm_ax = arm_imu.acceleration[0]
    arm_ay = arm_imu.acceleration[1]
    arm_az = arm_imu.acceleration[2]

    arm_mx, arm_my, arm_mz = arm_imu.magnetic
    
    hand_pitch = math.atan2(hand_az, hand_ax) * 180 / math.pi
    hand_roll = math.atan2(hand_az, hand_ay) * 180 / (math.pi);
    filtered_hand_mx = low_pass_filter(hand_mx, filtered_hand_mx)
    filtered_hand_my = low_pass_filter(hand_my, filtered_hand_my)
    hand_yaw =  90 - math.atan2(filtered_hand_my, filtered_hand_mx) * 180 / math.pi
    
    arm_pitch = math.atan2(arm_az, arm_ax) * 180 / math.pi
    arm_roll = math.atan2(arm_az, arm_ay) * 180 / math.pi
    arm_yaw = math.atan2(arm_my, arm_mx) * 180 / math.pi
    filtered_arm_mx = low_pass_filter(arm_mx, filtered_arm_mx)
    filtered_arm_my = low_pass_filter(arm_my, filtered_arm_my)
    arm_yaw = 90 - math.atan2(filtered_arm_my, filtered_arm_mx) * 180 / math.pi

    # angles in relation to arm IMU
    roll_diff = abs(abs(round(arm_roll - hand_roll)) - user_flexion_offset)
    pitch_diff = abs(round(arm_pitch - hand_pitch))
    yaw_diff = abs(abs(round(((arm_yaw - hand_yaw) + 180) % 360 - 180)) - user_radial_offset)

    if (roll_diff > 35 or roll_diff < -35) or (yaw_diff > 35 or yaw_diff < -35):
        red_led()
    else:
        green_led()

    return roll_diff, pitch_diff, yaw_diff


# set up c button interrupt after calibration so the user can set an offset (roll and yaw)
def user_offset_button(c_button):
    global set_offset_flag
    print("OFFSET BUTTON PRESSED")
    set_offset_flag = 1
c_button.irq(trigger=c_button.IRQ_RISING, handler=user_offset_button)


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
BLE_ADVERTISING_INTERVAL = 500


def encode_message(message):
    return message.encode('utf-8')


async def get_imu_data():
    
    roll_diff, pitch_diff, yaw_diff = calc_wrist_angles()
    
    # Data structure: message = f"device,roll,pitch,yaw"
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
        await asyncio.sleep(0.5)
        characteristic.write(msg)
        await asyncio.sleep(0.5)

    except Exception as e:
        print(f"writing error {e}")


full_battery = 4.2                  # these are our reference voltages for a full/empty battery, in volts
empty_battery = 3.0                 # the values could vary by battery size/manufacturer so you might need to adjust them

async def run_peripheral_mode():
    global user_radial_offset, user_flexion_offset, set_offset_flag, full_battery, empty_battery
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
            print("Sleeping for 4 seconds.\n")
            
        # read battery level
        vsys = ADC(Pin(29))                 # reads the system input voltage
        charging = Pin(24, Pin.IN)          # reading GP24 tells us whether or not USB power is connected
        conversion_factor = 3 * 3.3 / 65535
        voltage = vsys.read_u16() * conversion_factor
        percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
        if percentage > 100:
            percentage = 100.00
        if (charging.value != 1) and (percentage <= 10):
            for x in range(0,11):   # flash red when low battery
                if x%2 == 0:
                    red_led()
                else:
                    led_off()
            time.sleep(0.3)
        led_off()    
        #await asyncio.sleep(1)

        if set_offset_flag == 1:  # break out so offset can be calculated outside of advertise
            break


async def main():
    global user_flexion_offset, user_radial_offset, set_offset_flag
    blue_led()
    while True:
        tasks = [
            asyncio.create_task(run_peripheral_mode()), # run the run_peripheral_mode() function asynchronously
        ]    
        await asyncio.gather(*tasks)

        if set_offset_flag == 1:
            print("setting new offset")
            user_flexion_offset, pitch_unused, user_radial_offset = calc_wrist_angles()
            set_offset_flag = 0

asyncio.run(main())