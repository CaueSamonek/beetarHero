import time
from RPLCD import CharLCD
from RPi import GPIO
GPIO.setwarnings(False)

# cria LCD de forma limpa
def createLCD():
    return CharLCD(
        numbering_mode=GPIO.BCM,
        cols=16,
        rows=2,
        pin_rs= 26,
        pin_e = 19,
        pins_data=[25, 24, 22, 27],
        charmap='A00'
    )

time.sleep(0.5)
lcd = createLCD()
time.sleep(0.5)
lcd.clear()
lcd.home()


# funcoes wrappers
def clear():
    lcd.clear()

    for i in range(2):
        lines[i] = ""
        last[i] = ""
        scroll[i] = 0

def home():
    lcd.home()

def reset():
    clear()
    lcd.home()

def write(string):
    t = string.split('\n', 1)
    setLine(0, t[0])
    setLine(1, '')
    if len(t) > 1:
        setLine(1, t[1])

    update()

lines = ["", ""]
last = ["", ""]
scroll = [0, 0]
def setLine(row, text):
    lines[row] = text.strip()

    if text != lines[row]:
        lines[row] = text
        scroll[row] = 0
        last[row] = ""

lastScroll = time.time()
def update():
    global lastScroll

    now = time.time()

    if now - lastScroll > 0.5:
        lastScroll = now

        for i in range(2):
            if len(lines[i]) > 16:
                scroll[i] += 1

    for i in range(2):
        text = lines[i]

        if len(text) <= 16:
            show = text.ljust(16)
        else:
            loop = text + "   "
            pos = scroll[i] % len(loop)
            show = (loop + loop)[pos:pos + 16]

        if show != last[i]:
            lcd.cursor_pos = (i, 0)
            lcd.write_string(show)
            last[i] = show
