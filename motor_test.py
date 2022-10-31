import cv2
import RPi.GPIO as GPIO
import sys


#GPIO初期設定------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

#左
p1 = GPIO.PWM(17, 50) #50Hz
p2 = GPIO.PWM(22, 50) #50Hz
  

duty = 80
            
p1.start(0) 
p2.start(0)  
#------------------------


try:
    while True:
    #モーター制御------------------
        #「e」キーが押されたら前進
        c = sys.stdin.read(1)
        if c == 'e':
            p1.ChangeDutyCycle(duty)
            p2.ChangeDutyCycle(0)
              
        #「d」キーが押されたら後退
        if c == 'd':
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(duty)

        #「q」キーが押されたら止まる
        if c == 'q':
            p1.ChangeDutyCycle(0)
            p2.ChangeDutyCycle(0)
        #-----------------------------


except KeyboardInterrupt:
    pass

GPIO.cleanup()

    