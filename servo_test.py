# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# RCサーボモータ用ライブラリ
# -----------------------------------------------------------
# 2019/12/30    修正,動作確認
# -----------------------------------------------------------


import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
import pigpio
import time
import subprocess

class servo:

    pi = pigpio.pi()

    servo_pin = 0

    angle_min = -90.0
    angle_max = 90.0
    width_min = 500
    width_max = 2400

    angle_data = 0.0
    width = 1500

    def init(self, pin, **data):
        self.servo_pin = pin
        self.pi.set_mode(self.servo_pin, pigpio.OUTPUT)
        self.set_angle(0)
        if 'width_min' in data:
            self.width_min = data['width_min']
        if 'width_max' in data:
            self.width_max = data['width_max']
        if 'angle_min' in data:
            self.angle_min = data['angle_min']
        if 'angle_max' in data:
            self.angle_max = data['angle_max']
        # subprocess.run(['sudo', 'pigpiod'])

    def end(self):
        self.set_angle(0)
        from time import sleep
        sleep(0.1)
        self.pi.set_mode(self.servo_pin, pigpio.INPUT)
        #self.pi.stop() # ファイナライズ

    def home_position(self):
        center_width = (self.width_max + self.width_min) /2
        self.pi.set_servo_pulsewidth(self.servo_pin, center_width)

    def set_angle(self, angle):
        if self.angle_min <= angle <= self.angle_max:
            self.angle_data = angle
            self.update_servo()
            return True
        else:
            print(str(angle) + " is out of range")
            return False

    def angle_inc(self, angle):
        if self.angle_min <= self.angle_data + angle <= self.angle_max:
            self.angle_data += angle
            self.update_servo()

    def angle_dec(self, angle):
        if self.angle_min <= self.angle_data - angle <= self.angle_max:
            self.angle_data -= angle
            self.update_servo()           
        
    def update_servo(self):
        angle_range = self.angle_max - self.angle_min
        width_range = self.width_max - self.width_min
        absolute_angle = self.angle_data - self.angle_min
        self.width = self.width_min + absolute_angle * (width_range / angle_range)
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)
        time.sleep(0.1)

    def calibration(self):

        print("===== calibration =====")
        
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width_min)
        print("Please input now angle (min): ")
        self.angle_min = float(input())

        self.pi.set_servo_pulsewidth(self.servo_pin, self.width_max)
        print("please input now angle (max):")
        self.angle_max = float(input())

        print("angle max = " + str(self.angle_max))
        print("angle min = " + str(self.angle_min))

        print("=======================")


#黄色の検出
def ball_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ボールのHSVの値域
    hsv_min = np.array([25,100,100])
    hsv_max = np.array([35,255,255])
    mask = cv2.inRange(hsv, hsv_min, hsv_max)

    #ノイズ除去
    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    
    return closing

# ボール領域の座標取得
def analysis_blob_ball(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

    # 特徴抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0) #背景の情報削除

    # 面積最大のインデックス
    max_index = np.argmax(data[:, 4])

    # 情報格納用
    maxblob = {}

    # 各種情報を取得
    maxblob["upper_left"] = (data[:, 0][max_index], data[:, 1][max_index]) # 左上座標
    maxblob["width"] = data[:, 2][max_index]  # 幅
    maxblob["height"] = data[:, 3][max_index]  # 高さ
    maxblob["area"] = data[:, 4][max_index]   # 面積
    maxblob["center"] = center[max_index]  # 中心座標

    return maxblob


if __name__ == '__main__':

    #カメラ設定
    cap=cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    print("Camera start")

    #サーボ設定
    servo_PIN1 = 13
    #servo_PIN2 = 18

    servo_x = servo()
    #servo_y = servo()
    servo_x.init(servo_PIN1, angle_min=-90.0, angle_max=90.0)
    #servo_y.init(servo_PIN2, angle_min=-90.0, angle_max=90.0)


    servo_x.set_angle(0)
    now_angle_x = 0
    now_angle_y = 0

    try:

        print("Please input angle")

        while True:
            ret,frame=cap.read()    

            #img = ball_detect(frame)
            #target_ball = analysis_blob_ball(img)


            img = ball_detect(frame)
            target_ball = analysis_blob_ball(img)

            mean_x = int(target_ball["center"][0])
            mean_y = int(target_ball["center"][1])
                
            cv2.circle(frame,(mean_y,mean_x),10,(0,0,255),-1)
            
            angle_y = (160 - mean_y)*0.1
            #angle_y = -(mean_y - 120)/120.0*7
            
            if angle_y >= 0:
                servo_x.angle_dec(angle_y)
            else:
                servo_x.angle_inc(angle_y)
            #servo_y.set_angle(now_angle_y + angle_y)
            #now_angle_y = now_angle_y + angle_y
            #now_angle_x = now_angle_x + angle_x

            cv2.imshow('frame',frame)
            cv2.waitKey(1)
            #angle = int(input('angle:'))
            #servo.set_angle(angle)

    except KeyboardInterrupt:
        pass

    finally:
        servo_x.end()
        #servo_y.pi.stop()
        servo_x.end()
        #servo_y.pi.stop()
        cap.release()
        cv2.destroyAllWindows()