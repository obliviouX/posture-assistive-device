# Shows the available RAM. PEN_RGB332 is an 8 bit, fixed 256 colour palette which conserves your RAM.
# Try switching the pen_type to PEN_RGB565 (16 bit, 65K colour) and see the difference!
# If you have a Display Pack 2.0" or 2.8" use DISPLAY_PICO_DISPLAY_2 instead of DISPLAY_PICO_DISPLAY

import gc
import time
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332

display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332, rotate=0)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()

button_a = Pin(12, Pin.IN)
button_b = Pin(13, Pin.IN)
button_x = Pin(14, Pin.IN)
button_y = Pin(15, Pin.IN)

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

selected_menu = 0
selected_sub_menu = 0   # default sub menu for the 'b' button

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
    
    
def update_left_wrist():
    global lw_fe, lw_r, selected_menu, selected_sub_menu

    if selected_menu == 0:
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
    
    elif selected_menu == 1:

    elif selected_menu == 3:

    else: # display nothing


def update_right_wrist():
    global rw_fe, rw_r, selected_menu, selected_sub_menu
    
    if selected_menu == 0:
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

    elif selected_menu == 1:
    
    elif selected_menu == 3:
    
    else: # display nothing


def update_neck():
    global neck_fe, selected_menu
    
    if selected_menu == 0:
        if (int(neck_fe) > 35) or (int(neck_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)
            
        text_width_neck_fe = display.measure_text(str(neck_fe), 1, 0, 0)
        display.text(str(neck_fe), (WIDTH//4) + (text_width_neck_fe), (HEIGHT//4), 100, 1, 0)

    elif selected_menu == 2:
        if (int(neck_fe) > 35) or (int(neck_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)

        text_width_neck_fe = display.measure_text(str(neck_fe), 1, 0, 0)
        display.text(str(neck_fe), (WIDTH//2) + (text_width_neck_fe), (HEIGHT//2), 100, 1, 0)

    else: # display nothing


# 5 Menus Total
# button a = Menu 0 LW, RW, B
# button b = Menu 1 LW, RW, and LW RW individual sub menus
# button x = Menu 2 B
# button y = Menu 3 green or red screen when any posture is broken

# Menu 0 (a)                        # Menu 1 (b)                        # Menu 2 (x)                        # Sub menu 3 (y) (also for RW)
#############################       #############################       #############################       #############################
#... LW      RW      B      #       #...     LW        RW       #       #...          B             #       #...          LW            #
#                           #       #                           #       #                           #       #                           #
# FE                        #       # FE                        #       #                           #       # FE                        #
#                           #       #                           #       # FE                        #       #                           #
# R                         #       # R                         #       #                           #       # R                         #
#                           #       #                           #       #                           #       #                           #
#############################       #############################       #############################       #############################
def create_display_layout(device):
    global lw_fe, lw_r, rw_fe, rw_r, neck_fe, selected_menu, selected_sub_menu

    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.set_thickness(3)
    display.set_font("sans")

    # MENU 0
    if (button_a.value() == 0) or (selected_menu == 0):
        selected_menu = 0
        display.text("LW", ((WIDTH//4) - 20), 25, 100, 1, 0)
        display.text("RW", (WIDTH//2), 25, 100, 1, 0)
        display.text("B", (((WIDTH//4) * 3) + 20), 25, 100, 1, 0)

        display.text("FE", 10, (HEIGHT//4), 100, 1, 0)
        display.text("R", 10, ((HEIGHT//4) * 3), 100, 1, 0)

        update_left_wrist()  # draw the numbers to the screen
        update_right_wrist()
        update_neck()

    # MENU 1
    if button_b.value() == 0:
        selected_menu = 1
        selected_sub_menu = selected_sub_menu + 1

        if selected_sub_menu > 2:   # rollover check
            selected_sub_menu = 0

        if selected_sub_menu == 0:
            display.text("LW", (WIDTH//3), 25, 100, 1, 0)
            display.text("RW", ((WIDTH//3) * 2), 25, 100, 1, 0)
            update_left_wrist()
            update_right_wrist()

        elif selected_sub_menu == 1:
            display.text("LW", (WIDTH//2), 25, 100, 1, 0)
            update_left_wrist()
        
        elif selected_sub_menu == 2:
            display.text("RW", (WIDTH//2), 25, 100, 1, 0)
            update_right_wrist()
        
        else:
            display.text("sub menu error", (WIDTH//2), 25 100, 1, 0)

    # MENU 2
    if button_x.value() == 0:
        selected_menu = 2
        update_neck()

    # MENU 3
    if button_y.value() == 0:
        selected_menu = 3

    show_connected_device(device)


def update_display(fe, rad, device):  #flexion extension, radial, device
    global lw_fe, lw_r, rw_fe, rw_r, neck_fe

    if device == "1":   # update the global variables
        lw_fe = fe
        lw_r = rad
    elif device == "2":
        rw_fe = fe
        rw_r = rad
    elif device == "3":
        neck_fe = fe

    create_display_layout(device)

    display.update()
    #time.sleep(1.0 / 60)

        
def display_startup():
    display.set_pen(BLACK)
    display.set_pen(BLUE)
    display.set_thickness(3)
    display.set_font("sans")
    text_width_searching = display.measure_text("Searching...", 1, 0, 0)
    display.text("Searching...", (WIDTH//3) + 20, 210, 100, 1, 0)
    