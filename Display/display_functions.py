# Shows the available RAM. PEN_RGB332 is an 8 bit, fixed 256 colour palette which conserves your RAM.
# Try switching the pen_type to PEN_RGB565 (16 bit, 65K colour) and see the difference!
# If you have a Display Pack 2.0" or 2.8" use DISPLAY_PICO_DISPLAY_2 instead of DISPLAY_PICO_DISPLAY

import gc
import time
from machine import Pin
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_RGB332

display = PicoGraphics(DISPLAY_PICO_DISPLAY_2, pen_type=PEN_RGB332, rotate=0)

# set up constants for drawing
WIDTH, HEIGHT = display.get_bounds()

button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# interrupts for each button
def callback_a(button_a):
    global selected_menu
    print("button a pressed")
    selected_menu = 0
button_a.irq(trigger=button_a.IRQ_RISING, handler=callback_a)

def callback_b(button_b):
    global selected_menu, selected_sub_menu
    print("button b pressed")
    selected_menu = 1
    selected_sub_menu += 1
    if selected_sub_menu > 2:
        selected_sub_menu = 0
button_b.irq(trigger=button_b.IRQ_RISING, handler=callback_b)

def callback_x(button_x):
    global selected_menu
    print("button x pressed")
    selected_menu = 2
button_x.irq(trigger=button_x.IRQ_RISING, handler=callback_x)

def callback_y(button_y):
    global selected_menu
    print("button y pressed")
    selected_menu = 3
button_y.irq(trigger=button_y.IRQ_RISING, handler=callback_y)


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
lw_fe = '999'   # if any of these is 999, it means it is not connected
lw_r = '999'    # so a dash can be displayed
rw_fe = '999'
rw_r = '999'
neck_fe = '999'

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
def create_display_layout():
    global lw_fe, lw_r, rw_fe, rw_r, neck_fe, selected_menu, selected_sub_menu

    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    display.set_thickness(3)
    display.set_font("sans")

    # MENU 0
    if selected_menu == 0:
        text_width = (display.measure_text("LW", 1))//2
        display.text("LW", ((WIDTH//4) - text_width), 25, 100, 1, 0)
        text_width = (display.measure_text("RW", 1))//2
        display.text("RW", ((WIDTH//5) * 3) - text_width, 25, 100, 1, 0)
        text_width = (display.measure_text("B", 1))//2
        display.text("B", ((WIDTH//6) * 5) - text_width, 25, 100, 1, 0)

        display.text("FE", 3, (HEIGHT//4), 100, 1, 0)
        display.text("R", 3, ((HEIGHT//4) * 3), 100, 1, 0)

        # left wrist values
        if (int(lw_fe) > 35) or (int(lw_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)
        
        text_width = (display.measure_text(str(lw_fe), 1))//2
        display.text(str(lw_fe), (WIDTH//4) - text_width, (HEIGHT//4), 100, 1, 0)
            
        if (int(lw_r) > 35) or (int(lw_r) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)

        text_width = (display.measure_text(str(lw_r), 1))//2
        display.text(str(lw_r), (WIDTH//4) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)

        # right wrist values
        if (int(rw_fe) > 35) or (int(rw_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)
        
        text_width = (display.measure_text(str(rw_fe), 1))//2
        display.text(str(rw_fe), ((WIDTH//5) * 3) - text_width, (HEIGHT//4), 100, 1, 0)
                
        if (int(rw_r) > 35) or (int(rw_r) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)
                
        text_width = (display.measure_text(str(rw_r), 1))//2
        display.text(str(rw_r), ((WIDTH//5) * 3) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)

        # back/neck values
        if (int(neck_fe) > 35) or (int(neck_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)

        text_width = (display.measure_text(str(neck_fe), 1))//2
        display.text(str(neck_fe), (((WIDTH//6) * 5) - text_width), (HEIGHT//4), 100, 1, 0)


    # MENU 1
    if selected_menu == 1:

        if selected_sub_menu == 0:
            text_width = (display.measure_text("LW", 1))//2
            display.text("LW", (WIDTH//3) - text_width, 25, 100, 1, 0)
            text_width = (display.measure_text("RW", 1))//2
            display.text("RW", ((WIDTH//3) * 2) - text_width, 25, 100, 1, 0)
            display.text("FE", 3, (HEIGHT//4), 100, 1, 0)
            display.text("R", 3, ((HEIGHT//4) * 3), 100, 1, 0)

            # left wrist values
            if (int(lw_fe) > 35) or (int(lw_fe) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)
            
            text_width = (display.measure_text(str(lw_fe), 1))//2
            display.text(str(lw_fe), (WIDTH//3) - text_width, (HEIGHT//4), 100, 1, 0)
            
            if (int(lw_r) > 35) or (int(lw_r) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)

            text_width = (display.measure_text(str(lw_r), 1))//2
            display.text(str(lw_r), (WIDTH//3) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)

            # right wrist values
            if (int(rw_fe) > 35) or (int(rw_fe) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)
            
            text_width = (display.measure_text(str(rw_fe), 1))//2
            display.text(str(rw_fe), ((WIDTH//3) * 2) - text_width, (HEIGHT//4), 100, 1, 0)
                
            if (int(rw_r) > 35) or (int(rw_r) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)
            
            text_width = (display.measure_text(str(rw_r), 1))//2
            display.text(str(rw_r), ((WIDTH//3) * 2) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)


        elif selected_sub_menu == 1:
            text_width = (display.measure_text("Left Wrist", 1))//2
            display.text("Left Wrist", (WIDTH//2) - text_width, 25, 100, 1, 0)
            display.text("FE", 3, (HEIGHT//4), 100, 1, 0)
            display.text("R", 3, ((HEIGHT//4) * 3), 100, 1, 0)

            if (int(lw_fe) > 35) or (int(lw_fe) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)
            
            text_width = (display.measure_text(str(lw_fe), 1))//2
            display.text(str(lw_fe), (WIDTH//2) - text_width, (HEIGHT//4), 100, 1, 0)
            
            if (int(lw_r) > 35) or (int(lw_r) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)

            text_width = (display.measure_text(str(lw_r), 1))//2
            display.text(str(lw_r), (WIDTH//2) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)
        
        elif selected_sub_menu == 2:
            text_width = (display.measure_text("Right Wrist", 1))//2
            display.text("Right Wrist", (WIDTH//2) - text_width, 25, 100, 1, 0)
            display.text("FE", 3, (HEIGHT//4), 100, 1, 0)
            display.text("R", 3, ((HEIGHT//4) * 3), 100, 1, 0)

            if (int(rw_fe) > 35) or (int(rw_fe) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)

            text_width = (display.measure_text(str(rw_fe), 1))//2
            display.text(str(rw_fe), (WIDTH//2) - text_width, (HEIGHT//4), 100, 1, 0)
                
            if (int(rw_r) > 35) or (int(rw_r) < -35):
                display.set_pen(RED)
            else:
                display.set_pen(GREEN)

            text_width = (display.measure_text(str(rw_r), 1))//2
            display.text(str(rw_r), (WIDTH//2) - text_width, ((HEIGHT//4) * 3), 100, 1, 0)
        
        else:
            display.text("sub menu error", (WIDTH//2), 25, 100, 1, 0)

    # MENU 2
    if selected_menu == 2:
        text_width = (display.measure_text("Back", 1))//2
        display.text("Back", (WIDTH//2) - text_width, 25, 100, 1, 0)

        if (int(neck_fe) > 35) or (int(neck_fe) < -35):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)

        text_width = (display.measure_text(str(neck_fe), 1))//2
        display.text(str(neck_fe), (WIDTH//2) - text_width, (HEIGHT//2), 100, 1, 0)

    # MENU 3
    if selected_menu == 3:
        lw_fe = abs(int(lw_fe))
        lw_r = abs(int(lw_r))
        rw_fe = abs(int(rw_fe))
        rw_r = abs(int(rw_r))
        neck_fe = abs(int(neck_fe))

        if (lw_fe > 35) or (lw_r > 35) or (rw_fe > 35) or (rw_r > 35) or (neck_fe > 20):
            display.set_pen(RED)
        else:
            display.set_pen(GREEN)

        display.rectangle(0, 0, 320, 240)


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

    create_display_layout()
    show_connected_device(device)

    display.update()
    #time.sleep(1.0 / 60)


def display_startup():
    display.set_pen(BLACK)
    display.set_pen(BLUE)
    display.set_thickness(3)
    display.set_font("sans")
    text_width_searching = display.measure_text("Searching...", 1, 0, 0)
    display.text("Searching...", (WIDTH//3) + 20, 210, 100, 1, 0)
    