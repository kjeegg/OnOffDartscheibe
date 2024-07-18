import time
from PIL import Image, ImageDraw, ImageFont
from gpiozero import DigitalInputDevice, Button
from lib import LCD_1inch69  # Assuming this is your LCD library

# Initialize the display
disp = LCD_1inch69.LCD_1inch69()
disp.Init()
disp.clear()
disp.bl_DutyCycle(100)#Backlight auf 100% Helligkeit

Schriftart = ImageFont.truetype("./Font/Font02.ttf", 32)

#Rotary Encoder
clk_pin = 17
dt_pin = 22
sw_pin = 23

#GPIOZero initialisieren
clk = DigitalInputDevice(clk_pin)
dt = DigitalInputDevice(dt_pin)
button = Button(sw_pin)

current_position = 0
num_items = 0
selected_index = None
last_clk_state = clk.is_active
input_list = []  #Liste

def read_encoder():
    global current_position
    global last_clk_state

    clk_state = clk.is_active
    dt_state = dt.is_active

    if clk_state != last_clk_state:
        if dt_state != clk_state:
            current_position = (current_position + 1) % num_items
        else:
            current_position = (current_position - 1) % num_items
        last_clk_state = clk_state
        update_display()

'''
Wählt ein Element aus
'''
def on_button_press():
    global selected_index
    selected_index = current_position
    clear_display()#Cleared Display
    reset_encoder()

def update_display():
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    image1 = image1.rotate(-90, expand=True) #Lcd drehen weil seitwärts ausgerichted
    draw = ImageDraw.Draw(image1)

    for i in range(num_items):
        text = '> ' + input_list[i] if i == current_position else '  ' + input_list[i]
        y_position = i * 32 + 25
        draw.text((25, y_position), text, font=Schriftart, fill="BLACK")

    disp.ShowImage(image1)

def clear_display():
    disp.clear()


def reset_encoder():
    global last_clk_state
    last_clk_state = clk.is_active
    button.when_pressed = on_button_press

def lcdUserListSelect(lst):
    global current_position
    global num_items
    global selected_index
    global input_list

    #Zurücksetzen in Ausgangszustand
    input_list = lst  # Update the global input_list
    num_items = len(input_list)
    current_position = 0
    selected_index = None
    reset_encoder()
    clear_display()
    update_display()

    # Polling loop
    while selected_index is None:
        read_encoder()
        time.sleep(0.01)  # Adjust delay for responsiveness

    clear_display()
    return selected_index