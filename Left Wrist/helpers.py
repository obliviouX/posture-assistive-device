from machine import Pin, PWM
import math
from utime import sleep

# RGB LED SETUP
red_pin = Pin(13)
green_pin = Pin(14)
blue_pin = Pin(15)

red_pwm = PWM(red_pin, freq=1000)
green_pwm = PWM(green_pin, freq=1000)
blue_pwm = PWM(blue_pin, freq=1000)

filtered_hand_mx = 0.0 
filtered_hand_my = 0.0
filtered_arm_mx = 0.0 
filtered_arm_my = 0.0

def rgb_led(r_value, g_value, b_value): # to set rgb values easier (values from 0 to 65535)
    red_pwm.duty_u16(r_value)
    green_pwm.duty_u16(g_value)
    blue_pwm.duty_u16(b_value)

def red_led():      # for bad posture
    red_pwm.duty_u16(30000)
    green_pwm.duty_u16(0)
    blue_pwm.duty_u16(0)

def green_led():    # for good posture
    red_pwm.duty_u16(0)
    green_pwm.duty_u16(30000)
    blue_pwm.duty_u16(0)

def blue_led():     # for bluetooth
    red_pwm.duty_u16(0)
    green_pwm.duty_u16(0)
    blue_pwm.duty_u16(10000)

def blue_green_led():   # to show device has started
    red_pwm.duty_u16(0)
    green_pwm.duty_u16(15000)
    blue_pwm.duty_u16(30000)

def purple_led():   # to show calibration
    red_pwm.duty_u16(10000)
    green_pwm.duty_u16(0)
    blue_pwm.duty_u16(10000)

def led_off():      # turn off led
    red_pwm.duty_u16(0)
    green_pwm.duty_u16(0)
    blue_pwm.duty_u16(0)

def declare_globals():
    global pitch_diff, yaw_diff, roll_diff
    pitch_diff = 0
    yaw_diff = 0
    roll_diff = 0


def low_pass_filter(raw_value:float, remembered_value):
    ''' Only applied 20% of the raw value to the filtered value '''
    
    # global filtered_value
    alpha = 0.8
    filtered = 0
    filtered = (alpha * remembered_value) + (1.0 - alpha) * raw_value
    return filtered
