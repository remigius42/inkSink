<!-- spellchecker:ignore getbuffer setmode -->

# Build Guide Code Snippets

Starting points from the build guide. Not production-ready — use as reference
for the implementation, not verbatim.

## Display (`core/display.py`)

```python
import subprocess
from PIL import Image
from waveshare_epd import epd7in5_V2

def render_card_html(html_content):
    """Convert HTML card to e-ink image"""
    html_template = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Noto Sans CJK JP', sans-serif;
                font-size: 24px;
                padding: 20px;
                width: 760px;
            }}
        </style>
    </head>
    <body>{html_content}</body>
    </html>
    """

    with open('/tmp/card.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

    subprocess.run([
        'wkhtmltoimage',
        '--width', '800',
        '--height', '480',
        '--encoding', 'utf-8',
        '/tmp/card.html',
        '/tmp/card.png'
    ])

    img = Image.open('/tmp/card.png').convert('1')
    return img

def display_card(epd, image):
    """Update e-ink display with partial refresh"""
    epd.init()
    epd.display_Partial(epd.getbuffer(image))
```

### Notes

- `epd7in5_V2` is the correct module for the Waveshare 7.5" V2 HAT
- `display_Partial()` for card transitions (~0.4s); `display()` for full refresh
- `getbuffer()` converts PIL image to the format the driver expects
- The renderer design moves HTML templating to `core/renderer.py` and display
  calls to `core/display.py` — don't conflate them as above

## Input (`core/input.py`)

```python
import RPi.GPIO as GPIO
import time

BUTTONS = {
    'power': 4,
    'show_answer': 12,
    'again': 13,
    'hard': 16,
    'good': 19,
    'easy': 26
}

GPIO.setmode(GPIO.BCM)
for pin in BUTTONS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def wait_for_button():
    """Wait for any button press with debouncing"""
    while True:
        for name, pin in BUTTONS.items():
            if GPIO.input(pin) == False:  # LOW when pressed
                time.sleep(0.05)  # 50ms debounce
                if GPIO.input(pin) == False:
                    return name
        time.sleep(0.01)  # 10ms polling interval
```
