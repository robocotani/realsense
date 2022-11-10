import numpy as np
import cv2
import RPi.GPIO as GPIO
import pyrealsense2.pyrealsense2 as rs
import time
import M_flag


#距離計測用関数
def distance(center_x,center_y):
    #ボールとの距離は角度を補正
    #周囲の5点を取って平均
    #かけ離れている点は除外
    dist = []

    for i in range(5):
        for j in range(5):
            dist1 = depth_frame.get_distance(center_x + i, center_y + j)
            dist.append(float(format(dist1,'.4f')))
    
    #3.5m以上の点は除外して平均
    dist_new = [i for i in dist if 0.1 < i < 3.5] 

    #ゼロ除算の対策
    dist_mean = sum(dist_new)/len(dist_new)

    return dist_mean


def right_rotation(duty):
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    


def left_rotation(duty):
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)


def move(duty):
    #正転
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)


def down(duty):
    #後転
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    

def stop():
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    
    


#GPIO初期設定------------
GPIO.setmode(GPIO.BCM)

PIN1 = 17
PIN2 = 22
PIN3 = 27
PIN4 = 18
    

GPIO.setup(PIN1, GPIO.OUT)
GPIO.setup(PIN2, GPIO.OUT)
GPIO.setup(PIN3, GPIO.OUT)
GPIO.setup(PIN4, GPIO.OUT)

#左
p1 = GPIO.PWM(PIN1, 50) #50Hz
p2 = GPIO.PWM(PIN2, 50) #50Hz
#右
p3 = GPIO.PWM(PIN3, 50) #50Hz
p4 = GPIO.PWM(PIN4, 50) #50Hz

duty = 80
            
p1.start(0) 
p2.start(0) 
p3.start(0) 
p4.start(0) 

#------------------------

#フラグの設定
flag = False #フラッグ検出
depth = False #距離計測
hole = False #打球

#画面サイズ設定
size_w = 1280
size_h = 720


# ストリーム(Color/Depth)の設定
config = rs.config()

config.enable_stream(rs.stream.color, size_w, size_h, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, size_w, size_h, rs.format.z16, 30)

# ストリーミング開始
pipeline = rs.pipeline()
profile = pipeline.start(config)

# Alignオブジェクト生成
align_to = rs.stream.color
align = rs.align(align_to)

try:
    while True:
        # フレーム待ち
        frames = pipeline.wait_for_frames()

        #座標の補正
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame or not color_frame:
            continue

        RGB_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

         #depth imageをカラーマップに変換
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)

        # 表示
        cv2.rectangle(RGB_image, ((size_w / 2) - 20, 0), ((size_w / 2) + 20, size_w), (0, 255, 0), 2)
        cv2.imshow('RealSense', RGB_image)
        

        k=cv2.waitKey(1)
        if k==ord('q'):#qで終
            cv2.destroyAllWindows()
            GPIO.cleanup()
            pipeline.stop()
            break
        if k==ord('s'):#sを押すとスタート
            flag = True
            

        if flag == True:
            center_flag_x,center_flag_y,RGB_image = M_flag.flag_detect(RGB_image)
            cv2.imshow('mask',RGB_image)

            if center_flag_x == None:
                #フラッグ未検出
                print("未検出")
                right_rotation(20)
                pass
            elif center_flag_x < (size_w / 2) - 20:
                left_rotation(10) #左回転
                cv2.circle(RGB_image,(center_flag_x,center_flag_y),2,(0,255,0),3)
                
                print('left')
                time.sleep(1)
            elif center_flag_x > (size_w / 2) + 20:
                right_rotation(10) #右回転
                print('right')
                time.sleep(1)
            elif (size_w / 2) - 20 <= center_flag_x <= (size_w / 2) + 20:
                #停止
                print('stop')
                flag = False
                hole = True
            else:
                pass
          
            
        if hole == True:
	
            dist_depth = distance(center_flag_x,center_flag_y)
            
            print(dist_depth)
            print("打球")

            
            hole = False
            flag = True

            
              
              
except KeyboardInterrupt:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
