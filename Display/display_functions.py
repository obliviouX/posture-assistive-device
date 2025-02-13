# Shows the available RAM. PEN_RGB332 is an 8 bit, fixed 256 colour palette which conserves your RAM.
# Try switching the pen_type to PEN_RGB565 (16 bit, 65K colour) and see the difference!
# If you have a Display Pack 2.0" or 2.8" use DISPLAY_PICO_DISPLAY_2 instead of DISPLAY_PICO_DISPLAY

import gc
import time
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332

display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332, rotate=0)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()

#button_a = Pin(12, Pin.IN, Pin.PULL_UP)
#button_b = Pin(13, Pin.IN, Pin.PULL_UP)
#button_x = Pin(14, Pin.IN, Pin.PULL_UP)
#button_y = Pin(15, Pin.IN, Pin.PULL_UP)

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255,255,255)
RED = display.create_pen(255,0,0)
GREEN = display.create_pen(0,255,0)
BLUE = display.create_pen(0,0,255)
LIGHT_BLUE = display.create_pen(0,50,255)
ULTRA_LIGHT_BLUE = display.create_pen(0,125,255)
YELLOW = display.create_pen(255,255,0)

# global variables so they can stay on the screen
# instead of removed when display is updated
lw_fe = 1000   # if any of these is 1000, it means it is not connected
lw_r = 1000    # so a dash can be displayed
rw_fe = 1000
rw_r = 1000
neck_fe = 1000

def show_connected_device(device):
    
    if device == "1":
        display.set_pen(BLUE)
        display.circle(10, 10, 3)
    elif device == "2":
        display.set_pen(LIGHT_BLUE)
        display.circle(16, 10, 3)
    elif device == "3":
        display.set_pen(ULTRA_LIGHT_BLUE)
        display.circle(22, 10, 3)
    else:
        display.set_pen(RED)
        display.circle(10,10,3)
    
    
def update_left_wrist(fe, rad):
    
    global lw_fe, lw_r
    lw_fe = fe
    lw_r = rad
    
    if (int(lw_fe) > 35) or (int(lw_fe) < -35):
        display.set_pen(RED)
    else:
        display.set_pen(GREEN)
        
    display.text(str(lw_fe), (WIDTH//4), (HEIGHT//4), 100, 1, 0)
        
    if (int(lw_r) > 35) or (int(lw_r) < -35):
        display.set_pen(RED)
    else:
        display.set_pen(GREEN)

    display.text(str(lw_r), (WIDTH//4), ((HEIGHT//4) * 3), 100, 1, 0)
        

def update_right_wrist(fe, rad):
    
    global rw_fe, rw_r
    rw_fe = fe
    rw_r = rad
    
    if (int(rw_fe) > 35) or (int(rw_fe) < -35):
        display.set_pen(RED)
    else:
        display.set_pen(GREEN)
        
    display.text(str(rw_fe), (WIDTH//2), (HEIGHT//4), 100, 1, 0)
        
    if (int(rw_r) > 35) or (int(rw_r) < -35):
        display.set_pen(RED)
    else:
        display.set_pen(GREEN)
        
    display.text(str(rw_r), (WIDTH//2), ((HEIGHT//4) * 3), 100, 1, 0)


def update_neck(fe):
    
    global neck_fe
    neck_fe = fe
    
    if (int(neck_fe) > 35) or (int(neck_fe) < -35):
        display.set_pen(RED)
    else:
        display.set_pen(GREEN)
        
    text_width_neck_fe = display.measure_text(str(neck_fe), 1, 0, 0)
    display.text(str(neck_fe), (WIDTH//4) + (text_width_neck_fe), (HEIGHT//4), 100, 1, 0)
    

def create_display_layout():
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)  # White
    display.set_thickness(3)
    display.set_font("sans")

    #text_width_lw = display.measure_text("LW", 4, 0, 0)
    #text_width_rw = display.measure_text("RW", 4, 0, 0)
    #text_width_b = display.measure_text("B", 4, 0, 0)
    
    #display.text(text, x, y, wordwrap, scale, angle, spacing)
    
    # Menu 1
    #############################
    #... LW      RW      B      #
    #                           #
    # FE                        #
    #                           #
    # R                         #
    #                           #
    #############################
    
    # Menu 2
    #############################
    #...     LW        RW       #
    #                           #
    # FE                        #
    #                           #
    # R                         #
    #                           #
    #############################
    
    # Menu 3
    #############################
    #...          B             #
    #                           #
    #                           #
    # FE                        #
    #                           #
    #                           #
    #############################
    
    display.text("LW", ((WIDTH//4) - 20), 25, 100, 1, 0)
    display.text("RW", (WIDTH//2), 25, 100, 1, 0)
    display.text("B", (((WIDTH//4) * 3) + 20), 25, 100, 1, 0)

    text_width_fe = display.measure_text("F/E", 1, 0, 0)
    text_width_r = display.measure_text("R", 1, 0, 0)
    display.text("FE", 10, (HEIGHT//4), 100, 1, 0)
    display.text("R", 10, ((HEIGHT//4) * 3), 100, 1, 0)


def update_display(fe, rad, device):  #flexion extension, radial, device

    create_display_layout()
    
    if device == "1":
        update_left_wrist(fe, rad)
    elif device == "2":
        update_right_wrist(fe, rad)
    elif device == "3":
        update_neck(fe)

    show_connected_device(device)
    
    display.update()
    #time.sleep(1.0 / 60)

#update_display(20,30)
        
def display_startup():
    display.set_pen(BLACK)
    display.set_pen(BLUE)
    display.set_thickness(3)
    display.set_font("sans")
    text_width_searching = display.measure_text("Searching...", 1, 0, 0)
    display.text("Searching...", (WIDTH//3) + 20, 210, 100, 1, 0)
    