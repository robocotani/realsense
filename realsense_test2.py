import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import RPi.GPIO as GPIO
import pyrealsense2.pyrealsense2 as rs
import time
import M_ball


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
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    time.sleep(0.01)


def right_rotation():
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    time.sleep(0.01)


def move():
    #正転
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    time.sleep(0.01)
    

def down():
    #後転
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    time.sleep(0.5)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    time.sleep(0.01)
    


#GPIO初期設定------------
GPIO.setmode(GPIO.BCM)

PIN1 = 17
PIN2 = 22
    

GPIO.setup(PIN1, GPIO.OUT)
GPIO.setup(PIN2, GPIO.OUT)

    #左
p1 = GPIO.PWM(PIN1, 50) #50Hz
p2 = GPIO.PWM(PIN2, 50) #50Hz
    

duty = 80
            
p1.start(0) 
p2.start(0) 
    #------------------------

    #フラグの設定
ball_1 = False #ボール位置へ移動 デプスカメラ
depth = False #距離計測
hole = False #打球




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
        
        img1 = RGB_image
        
        

        k=cv2.waitKey(1)
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            GPIO.cleanup()
            break
        if k==ord('s'):#sを押すと距離と画像を取得
            ball_1 = True
            
            #dist = depth_frame.get_distance(center_x, center_y)
            #print(dist)
            pass
            
        if ball_1 == True:
            center_ball_1_x,center_ball_1_y = M_ball.ball_detect(img1)

            if center_ball_1_x == None:
                    #ボール未検出
                    #ball_2 = True
                print("未検出")
                pass
            elif center_ball_1_x < 640:                    
                #left_rotation() #左回転
                print('left')
            elif center_ball_1_x > 640:                    
                #right_rotation() #右回転
                print('right')
            elif 600 <= center_ball_1_x <= 680:
                if center_ball_1_y == None:
                    #ボール未検出
                    pass
                elif center_ball_1_y < 360:
                    #down() #後転
                    print('down')
                elif center_ball_1_y > 360:                        
                    #move() #正転
                    print('move')
                elif 320 <= center_ball_1_y <= 400:
                    #範囲に入ったら停止
                    print('stop')
                    ball_1 = False
                    hole = True
                else:
                    pass
          
            
        if hole == True:
	
            dist_depth = distance(center_ball_1_x,center_ball_1_y)
            
            print(dist_depth)
            print("打球")

            hole = False
            ball_1 = True
              
              
finally:
    # ストリーミング停止
    pipeline.stop()
