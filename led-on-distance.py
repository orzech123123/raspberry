import RPi.GPIO as GPIO
import time

# --- Ultrasonic Sensor Setup ---
# Board numbering system to use
GPIO.setmode(GPIO.BCM)

# Setup trigger and echo pins
TRIG_PIN = 23
ECHO_PIN = 24
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# --- LED Setup ---
LED_PIN = 17
GPIO.setup(LED_PIN, GPIO.OUT)
# Initially turn off the LED
GPIO.output(LED_PIN, GPIO.LOW)

# --- Variables ---
DELAY_TIME_SENSOR = 0.2 # Delay between sensor readings
FADE_STEP_DELAY = 0.005 # Delay for LED fade steps

def measure_distance():
    """Measures the distance using the HC-SR04 ultrasonic sensor."""
    # Ensure trigger pin is low
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(2E-6)

    # Set trigger pin high for 10 microseconds to send ping
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(10E-6)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # Wait for echo pin to go high (ping sent)
    pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        # Add a timeout to prevent infinite loop if echo is never received
        if time.time() - pulse_start > 0.1: # Timeout after 0.1 seconds
            return -1 # Indicate an error or no reading

    # Wait for echo pin to go low (ping received)
    pulse_end = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        # Add a timeout
        if time.time() - pulse_end > 0.1:
            return -1

    pulse_duration = pulse_end - pulse_start

    # Speed of sound at 20°C (approx 68°F) is 343 meters/second.
    # We use 34300 cm/second. Divide by 2 because sound travels to target and back.
    distance_cm = (pulse_duration * 34300) / 2
    return distance_cm

def fade_led():
    """Fades the LED in and out using RPi.GPIO (simulated PWM)."""
    # This simulation is basic on/off and won't be as smooth as true PWM.
    # For true PWM with RPi.GPIO, you'd use GPIO.PWM.
    # For this example, we'll just blink it quickly to simulate fading if PWM isn't set up.
    # Or, a simpler approach for a quick blink is better here.
    # Let's just make it blink clearly for this scenario.

    # Blink for a short duration
    for _ in range(3): # Blink 3 times
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.1)

try:
    print("Starting distance measurement and LED control...")
    while True:
        dist_cm = measure_distance()

        if dist_cm != -1: # Check if a valid distance was measured
            print(f'Distance = {dist_cm:.1f} cm')

            if dist_cm < 15:
                print("Distance less than 15cm! Blinking LED.")
                fade_led() # Call the blinking function
            else:
                print("Distance 15cm or more. Turning off LED.")
                GPIO.output(LED_PIN, GPIO.LOW) # Turn off LED
        else:
            print("Could not get a distance reading. Retrying...")
            GPIO.output(LED_PIN, GPIO.LOW) # Ensure LED is off if no reading

        time.sleep(DELAY_TIME_SENSOR)

except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    GPIO.cleanup() # Clean up all GPIOs on exit
    print("GPIO cleanup complete.")