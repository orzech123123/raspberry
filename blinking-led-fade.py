import gpiozero
import time
from datetime import datetime

# Initialize a PWM LED on GPIO pin 17
led = gpiozero.PWMLED(17)

# Fade in and out continuously
try:
    while True:
        # Fade in: 0% to 100%
        for brightness in range(0, 101):
            led.value = brightness / 100
            time.sleep(0.005)
        
        # Fade out: 100% to 0%
        for brightness in range(100, -1, -1):
            led.value = brightness / 100
            time.sleep(0.005)
        
        # Print message with current date and time
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"fade out at {now}")
except KeyboardInterrupt:
    led.off()
    print("Stopped fading.")
