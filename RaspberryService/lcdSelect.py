import time
from PIL import Image, ImageDraw, ImageFont
from gpiozero import DigitalInputDevice, Button
from lib import LCD_1inch69

#Init display
disp = LCD_1inch69.LCD_1inch69()
disp.Init()
disp.clear()
disp.bl_DutyCycle(100)  # Backlight at 100% brightness

Schriftart = ImageFont.truetype("./Font/Font02.ttf", 32)

# Rotary Encoder
clk_pin = 17
dt_pin = 22
sw_pin = 23

# GPIOZero initialisieren
clk = DigitalInputDevice(clk_pin)
dt = DigitalInputDevice(dt_pin)
button = Button(sw_pin)

current_position = 0
num_items = 0
selected_index = None
last_clk_state = clk.is_active
input_list = []  # List for items
header_position = 0

def draw_text(draw, text, position, font, max_width, fill):
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        width, _ = draw.textsize(test_line, font=font)
        
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    y_position = position[1]
    for line in lines:
        draw.text((position[0], y_position), line, font=font, fill=fill)
        y_position += font.getsize(line)[1]

def update_display(header_text):
    global header_position
    image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
    image1 = image1.rotate(-90, expand=True)  # Rotation because of side image
    draw = ImageDraw.Draw(image1)
    
    
    header_width = disp.width - 20  #Margin
    header_lines = []

    #Überschrift sinvoll aufteilen auf Zeilen
    current_line = ""
    for char in header_text:
        test_line = current_line + char
        width, _ = draw.textsize(test_line, font=Schriftart)
        if width > header_width:
            header_lines.append(current_line)
            current_line = char
        else:
            current_line = test_line
    if current_line:
        header_lines.append(current_line)
    
    header_position = (header_position + 1) % len(header_lines)
    
    #Überschrift
    y_position = 0
    for i, line in enumerate(header_lines):
        draw.text((25, y_position), line, font=Schriftart, fill="BLACK")
        y_position += Schriftart.getsize(line)[1]  #Zeilenumbruch
    
    #Überschrift/Titel unterstreichen
    underline_y = y_position
    underline_start = 25
    underline_end = min(disp.width - 25, underline_start + header_width)
    draw.line([(underline_start, underline_y), (underline_end, underline_y)], fill="BLACK", width=2)
    
    #Listen Elemente zeichnen
    for i in range(num_items):
        text = '> ' + input_list[i] if i == current_position else '  ' + input_list[i]
        y_position = len(header_lines) * Schriftart.getsize(header_lines[0])[1] + i * Schriftart.getsize(text)[1] + 50  # Adjusted to leave space for the header
        draw.text((25, y_position), text, font=Schriftart, fill="BLACK")

    disp.ShowImage(image1)

def clear_display():
    disp.clear()

def reset_encoder(header_text):
    global last_clk_state
    last_clk_state = clk.is_active
    button.when_pressed = lambda: on_button_press(header_text)

def read_encoder(header_text):
    global current_position, last_clk_state

    clk_state = clk.is_active
    dt_state = dt.is_active

    if clk_state != last_clk_state:
        if dt_state != clk_state:
            current_position = (current_position + 1) % num_items
        else:
            current_position = (current_position - 1) % num_items
        last_clk_state = clk_state
        update_display(header_text)

def on_button_press(header_text):
    global selected_index
    selected_index = current_position
    clear_display()
    reset_encoder(header_text)

def lcdUserListSelect(lst, header_text):
    global current_position, num_items, selected_index, input_list

    # Reset
    input_list = lst
    num_items = len(input_list)
    current_position = 0
    selected_index = None
    reset_encoder(header_text)
    clear_display()
    update_display(header_text)

    #Warten auf Nutzerinput
    while selected_index is None:
        read_encoder(header_text)
        
    blank_image = Image.new("RGB", (disp.width, disp.height), "WHITE")
    blank_image = blank_image.rotate(-90, expand=True)
    disp.ShowImage(blank_image)
    clear_display()
    return selected_index
