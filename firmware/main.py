from settings import *
import time
from machine import Timer


motor2.torque_enabled = False
motor2.operating_mode = 5
motor2.current_limit = 100
motor2.torque_enabled = True

count = 0
quarter_turn = 4096  # Assuming 4096 ticks per full rotation
last_pos = motor2.current_position

def turn(timer=-1):
    global count, motor2, quarter_turn, last_pos
    pos = motor2.current_position
    motor2.goal_extend_position = pos + quarter_turn  # Hold current position
    # print("Moving to position:", pos, pos + quarter_turn)
    print("error:", pos, motor2.goal_extend_position, pos - last_pos - quarter_turn)
    last_pos = pos
    count += 1
    if count >= 4:
        quarter_turn *= -1  # Reverse direction
        count = 0


tim = Timer(mode=Timer.PERIODIC, period=5000, callback=turn)  # Keep the timer running for time.ticks_ms()
print("start...")


isclosed = False if limiter.value() == 1 else True

print("Initial state, isclosed:", isclosed)

def limiter_handler(pin):
    global motor, isclosed
    if pin.value() == 0:  # Limiter activated
        motor.goal_pwm = 0
        motor.torque_enabled = False
        isclosed = True
        pin.irq(None)  # Disable IRQ to prevent multiple triggers


while True:
    if isclosed:
        motor.torque_enabled = False
        motor.operating_mode=4
        goal = motor.current_position + 7200 # -3900
        motor.torque_enabled = True
        print("Homing...")
        motor.goal_extend_position = goal  # Hold current position
        # while motor.current_position > goal + 10: 
        while motor.current_position < goal - 10: 
            time.sleep(0.1)
        motor.torque_enabled = False  # Disable torque
        print("opened!")
        isclosed = False
        time.sleep(2)
    else:
        while limiter.value() == 0:
            time.sleep(0.1)
        # limiter.callback = limiter_handler
        limiter.irq(trigger=Pin.IRQ_FALLING, handler=limiter_handler)
        motor.operating_mode=16
        motor.torque_enabled = True
        motor.goal_pwm = -400 # 550
        while limiter.value() == 1:
            time.sleep(0.1)
            print("closing...")
        print("closed!")






