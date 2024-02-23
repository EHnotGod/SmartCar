# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()
from machine import Pin, PWM
import time

b = 0
K1 = Pin(35, Pin.IN)
K2 = Pin(34, Pin.IN)
# K1用于使小车开始运动、K2用于使程序接入电脑时能手动停止（等同于Ctrl+C）、复位键使小车停下
# 175，250，60对应中间、右转最大量、左转最大量
# 弯道速度1-800，直道1-1000
while 1:
    if K1.value() == 0 and b == 0:
        b = 1

        led1 = PWM(Pin(26))
        led2 = PWM(Pin(27))
        p2 = PWM(Pin(15), Pin.OUT)
        led1.freq(100)
        led2.freq(100)
        p2.freq(100)

        # 直线
        p2.duty(175)
        led1.duty(1023)
        led2.duty(1)
        time.sleep_ms(6000)

        # 弯道
        led1.duty(800)
        led2.duty(1)
        p2.duty(105)
        time.sleep_ms(1200)

        p2.duty(165)
        led1.duty(1023)
        led2.duty(1)
        time.sleep_ms(1800)

        led1.duty(800)
        led2.duty(1)
        p2.duty(60)
        time.sleep_ms(2000)

        p2.duty(245)
        led1.duty(1)
        led2.duty(1023)
        time.sleep_ms(1100)

        led1.duty(800)
        led2.duty(1)
        p2.duty(98)
        time.sleep_ms(3400)

        p2.duty(170)
        led1.duty(1023)
        led2.duty(1)
        time.sleep_ms(6000)

        # 倒车

        led1.duty(1)
        led2.duty(800)
        p2.duty(60)
        time.sleep_ms(4000)

        led1.duty(1)
        led2.duty(1000)
        p2.duty(175)
        time.sleep_ms(4000)

        led1.duty(1000)
        led2.duty(1)
        p2.duty(175)
        time.sleep_ms(3200)

        led1.duty(800)
        led2.duty(1)
        p2.duty(60)
        time.sleep_ms(4000)

        led1.duty(1)
        led2.duty(1000)
        p2.duty(175)
        time.sleep_ms(1500)

        led1.duty(800)
        led2.duty(1)
        p2.duty(80)
        time.sleep_ms(3000)

        led1.duty(800)
        led2.duty(1)
        p2.duty(100)
        time.sleep_ms(3000)

        led1.duty(800)
        led2.duty(1)
        p2.duty(175)
        time.sleep_ms(6000)

        led1.duty(1)

    if K1.value() == 1 and b == 1:
        b = 0
    if K2.value() == 0:
        break



