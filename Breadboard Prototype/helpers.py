from machine import Pin, PWM
import math
from utime import sleep

# RGB LED SETUP
red_pin = Pin(15)
green_pin = Pin(14)
blue_pin = Pin(13)

red_pwm = PWM(red_pin, freq=1000)
green_pwm = PWM(green_pin, freq=1000)
blue_pwm = PWM(blue_pin, freq=1000)

filtered_hand_mx = 0.0 
filtered_hand_my = 0.0
filtered_arm_mx = 0.0 
filtered_arm_my = 0.0

def rgb_led(r_value, g_value, b_value): # to set rgb values easier
    red_pwm.duty_u16(r_value)
    green_pwm.duty_u16(g_value)
    blue_pwm.duty_u16(b_value)

def declare_globals():
    global pitch_diff, yaw_diff, roll_diff
    pitch_diff = 0
    yaw_diff = 0
    roll_diff = 0


def calc_wrist_angles(hand_ax, hand_ay, hand_az, arm_ax, arm_ay, arm_az, hand_mx, hand_my, hand_mz, arm_mx, arm_my, arm_mz):
    global filtered_hand_mx, filtered_hand_my, filtered_arm_mx, filtered_arm_my
    # roll (flexion/extension), yaw (radial)
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
    roll_diff = round(arm_roll - hand_roll)
    pitch_diff = round(arm_pitch - hand_pitch)
    yaw_diff = round(((arm_yaw - hand_yaw) + 180) % 360 - 180)

    # testing
    #print(" " * 100, end='\r')  # Clear the line (print spaces)
    #print("Hand Roll: ", roll_diff, "\t", "Hand Pitch: ", pitch_diff, "\t", " Hand Yaw: ", yaw_diff, "\t", "       ", end="\r")

    if (roll_diff > 35 or roll_diff < -35) or (yaw_diff > 35 or yaw_diff < -35):
        rgb_led(5000, 0, 0)
    else:
        rgb_led(0, 5000, 0)

    return roll_diff, pitch_diff, yaw_diff



def low_pass_filter(raw_value:float, remembered_value):
    ''' Only applied 20% of the raw value to the filtered value '''
    
    # global filtered_value
    alpha = 0.8
    filtered = 0
    filtered = (alpha * remembered_value) + (1.0 - alpha) * raw_value
    return filtered