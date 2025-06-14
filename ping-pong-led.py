import gpiozero
import time
import os
import sys
import termios
import tty
import select

# Initialize LED on GPIO 17
led = gpiozero.LED(17)

HEIGHT = 10
WIDTH = 20
PADDLE_LENGTH = 4

paddle_pos = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dir_x, ball_dir_y = 1, 1

def draw():
    os.system('clear')
    for y in range(HEIGHT):
        line = ''
        for x in range(WIDTH):
            if x == 0 and paddle_pos <= y < paddle_pos + PADDLE_LENGTH:
                line += '|'
            elif x == ball_x and y == ball_y:
                line += 'O'
            elif x == WIDTH - 1:
                line += '|'
            else:
                line += ' '
        print(line)

def get_key():
    '''Non-blocking key press detection'''
    dr, dw, de = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

def main():
    global paddle_pos, ball_x, ball_y, ball_dir_x, ball_dir_y

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    led_on_time = None

    try:
        tty.setcbreak(fd)
        print("Use W (up) and S (down) to move paddle. Ctrl+C to quit.")
        while True:
            key = get_key()
            if key:
                if key.lower() == 'w' and paddle_pos > 0:
                    paddle_pos -= 1
                elif key.lower() == 's' and paddle_pos < HEIGHT - PADDLE_LENGTH:
                    paddle_pos += 1

            ball_x += ball_dir_x
            ball_y += ball_dir_y

            if ball_y == 0 or ball_y == HEIGHT - 1:
                ball_dir_y *= -1

            if ball_x == 1 and paddle_pos <= ball_y < paddle_pos + PADDLE_LENGTH:
                ball_dir_x *= -1

            if ball_x < 0:
                ball_x, ball_y = WIDTH // 2, HEIGHT // 2
                ball_dir_x = 1

            if ball_x == WIDTH - 1:
                if led_on_time is None:
                    led.on()
                    led_on_time = time.time()
                ball_dir_x *= -1

            # Turn off LED after 500 ms without freezing
            if led_on_time is not None and (time.time() - led_on_time) >= 0.5:
                led.off()
                led_on_time = None

            draw()
            time.sleep(0.1)
    except KeyboardInterrupt:
        led.off()
        print("\nGame exited.")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
