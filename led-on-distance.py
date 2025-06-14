import RPi.GPIO as GPIO
import time
from collections import deque # Using deque for efficient history management

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
DELAY_TIME_SENSOR = 0.2  # Delay between sensor readings
# FADE_STEP_DELAY = 0.005 # Delay for LED fade steps (not used for simple ON/OFF)

# Define constants for better readability and adjustability
SPEED_OF_SOUND_CM_PER_S = 34300 # Speed of sound in cm/s at 20°C
MAX_DISTANCE_CM = 400          # Maximum reliable distance for HC-SR04
MIN_DISTANCE_CM = 2            # Minimum reliable distance for HC-SR04
TIMEOUT_S = 0.04               # Timeout for echo pulse (corresponds to ~686cm one-way travel)
                               # Use 0.04s for 400cm max range (400*2/34300 = 0.023s, so 0.04s is safe)

# --- History for Stable Readings ---
HISTORY_SIZE = 3 # Number of recent measurements to consider
distance_history = deque(maxlen=HISTORY_SIZE) # A deque automatically handles size

def measure_distance():
    """
    Measures the distance using the HC-SR04 ultrasonic sensor.
    Includes more robust timeout handling and distance filtering.
    Returns distance in cm, or -1 if no valid reading.
    """
    # Ensure trigger pin is low for a brief moment before sending the pulse
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.000002) # 2 microseconds

    # Set trigger pin high for 10 microseconds to send the sound ping
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.000010) # 10 microseconds
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time() # Initialize before waiting for the pulse
    pulse_end = time.time()   # Initialize before waiting for the pulse

    # Wait for echo pin to go high (start of the echo pulse)
    # Timeout if it doesn't go high within expected time
    start_time_wait = time.time()
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if (pulse_start - start_time_wait) > TIMEOUT_S:
            return -1 # Timeout waiting for pulse start

    # Wait for echo pin to go low (end of the echo pulse)
    # Timeout if it doesn't go low within expected time
    end_time_wait = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if (pulse_end - end_time_wait) > TIMEOUT_S:
            return -1 # Timeout waiting for pulse end

    pulse_duration = pulse_end - pulse_start

    # Calculate distance: (duration * speed of sound) / 2 (because sound travels to target and back)
    distance_cm = (pulse_duration * SPEED_OF_SOUND_CM_PER_S) / 2

    # Filter out unreliable readings:
    # 1. Distances smaller than the sensor's minimum reliable range (often caused by noise/internal reflection)
    # 2. Distances larger than the sensor's maximum reliable range (often caused by no echo/timeout)
    if distance_cm > MAX_DISTANCE_CM or distance_cm < MIN_DISTANCE_CM:
        return -1 # Indicate an invalid or out-of-range reading
    else:
        return distance_cm

def fade_led():
    """
    A simple blinking function for the LED.
    For true "fade," RPi.GPIO.PWM would be required, but this simulates it for quick feedback.
    """
    for _ in range(3): # Blink 3 times
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.1)

try:
    print("Starting distance measurement and LED control...")
    while True:
        dist_cm = measure_distance()

        if dist_cm != -1: # Check if a valid, in-range distance was measured
            print(f'Distance = {dist_cm:.1f} cm')
            # Add valid distance to history
            distance_history.append(dist_cm)

            # Check new condition: current distance < 15cm AND all last HISTORY_SIZE measurements < 15cm
            # The 'all' function will return True only if all elements in the deque satisfy the condition.
            # We also ensure the history has enough elements before checking.
            if dist_cm < 15 and len(distance_history) == HISTORY_SIZE and \
               all(d < 15 for d in distance_history):
                print(f"Distance < 15cm for last {HISTORY_SIZE} readings! Turning ON LED.")
                GPIO.output(LED_PIN, GPIO.HIGH)
                # You can uncomment fade_led() here if you prefer a blink on activation
                # fade_led()
            else:
                # If current distance is not < 15, or history is insufficient, or not all were < 15
                print("Condition not met to turn on LED. Turning OFF LED.")
                GPIO.output(LED_PIN, GPIO.LOW) # Turn off LED
        else:
            # If measure_distance returns -1, it means no valid, in-range reading was obtained
            print("Could not get a reliable distance reading (out of range or error). Turning OFF LED.")
            GPIO.output(LED_PIN, GPIO.LOW) # Ensure LED is off if no valid reading
            # Importantly, do NOT add -1 to the history. The history only tracks valid measurements.

        time.sleep(DELAY_TIME_SENSOR)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
finally:
    GPIO.cleanup() # Clean up all GPIOs on exit
    print("GPIO cleanup complete.")
