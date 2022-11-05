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
    dist1 = depth_frame.get_distance(center_x, center_y)
    dist2 = depth_frame.get_distance(center_x + 5, center_y + 5)
    dist3 = depth_frame.get_distance(center_x + 5, center_y - 5)
    dist4 = depth_frame.get_distance(center_x - 5, center_y + 5)
    dist5 = depth_frame.get_distance(center_x - 5, center_y - 5)
    
    dist.append(float(format(dist1,'.4f')))
    dist.append(float(format(dist2,'.4f')))
    dist.append(float(format(dist3,'.4f')))
    dist.append(float(format(dist4,'.4f')))
    dist.append(float(format(dist5,'.4f')))
    
    #3.5m以上の点は除外して平均
    
    dist_mean = sum(dist)/len(dist)

    return dist_mean


def left_rotation():
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(0.01)


def right_rotation():
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(0.01)


def move():
    #正転
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(0.01)
    

def down():
    #後転
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(0.01)
    


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


#カメラ設定----------------------------
#cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

#cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
#cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#--------------------------------------



# ストリーム(Color/Depth)の設定
config = rs.config()

config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# ストリーミング開始
pipeline = rs.pipeline()
profile = pipeline.start(config)

try:
    while True:
        # フレーム待ち
        frames = pipeline.wait_for_frames()

        #RGB
        RGB_frame = frames.get_color_frame()
        RGB_image = np.asanyarray(RGB_frame.get_data())

        #depyh
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)

        # 表示
        images = np.hstack((RGB_image, depth_colormap))
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.rectangle(RGB_image, (0, 320), (1280, 400), (0, 255, 0), 2)
        cv2.rectangle(RGB_image, (600, 0), (680, 720), (0, 255, 0), 2)
        
        #ret,frame2 = cap.read()
        #cv2.imshow('frame',frame2)

        img1 = RGB_image
        #img2 = frame2
        
        

        k=cv2.waitKey(1)
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            GPIO.cleanup()
            break
        if k==ord('s'):#sを押すとスタート
            ball_1 = True
            
            #dist = depth_frame.get_distance(center_x, center_y)
            #print(dist)
            

        if flag == True:
            center_flag_x,center_flag_y = M_flag.flag_detect(img1)

            if center_flag_x == None:
                #フラッグ未検出
                pass
            elif center_flag_x < 640:
                left_rotation() #左回転
            elif center_flag_x > 640:
                right_rotation() #右回転
            elif 600 <= center_flag_x <= 680:
                #停止
                flag = False
                cont = True
            else:
                pass
          
            
        if hole == True:
	
            dist_depth = distance(center_flag_x,center_flag_y)
            
            print(dist_depth)
            print("打球")

            if k==ord('d'):
                hole = False
                flag = True

            
              
              
finally:
    # ストリーミング停止
    pipeline.stop()
