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
    for i in range(5):
        for j in range(5):
            dist1 = depth_frame.get_distance(center_x + i, center_y + j)
            dist.append(float(format(dist1,'.4f')))
    
    
    #3.5m以上の点は除外して平均
    dist_new = [i for i in dist if 0.1 < i < 3.5] 

    dist_mean = sum(dist_new)/len(dist_new)

    return dist_mean


def right_rotation(duty):
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    # time.sleep(0.05)
    # #停止
    # p1.ChangeDutyCycle(0)
    # p2.ChangeDutyCycle(0)
    # p3.ChangeDutyCycle(0)
    # p4.ChangeDutyCycle(0)
    # time.sleep(0.1)


def left_rotation(duty):
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    # time.sleep(0.05)
    # #停止
    # p1.ChangeDutyCycle(0)
    # p2.ChangeDutyCycle(0)
    # p3.ChangeDutyCycle(0)
    # p4.ChangeDutyCycle(0)
    # time.sleep(0.1)


def move(duty):
    #
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    # time.sleep(0.1)
    # #停止
    # p1.ChangeDutyCycle(0)
    # p2.ChangeDutyCycle(0)
    # p3.ChangeDutyCycle(0)
    # p4.ChangeDutyCycle(0)
    # time.sleep(0.1)
    

def down():
    #
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    time.sleep(0.1)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(0.1)
    


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

duty = 30
            
p1.start(0) 
p2.start(0) 
p3.start(0) 
p4.start(0) 

#------------------------

#フラグの設定
ball_1 = False #ボール位置へ移動 デプスカメラ
ball_2 = True #下カメラ
#cont = False #ボール微調整
depth = False #距離計測
hole = False #打球

#画面サイズ設定
size_w = 1280
size_h = 720


#カメラ設定----------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

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

# Alignオブジェクト生成
align_to = rs.stream.color
align = rs.align(align_to)

print((size_w / 2) -20, (size_w / 2) +20)

try:
    while True:
        # フレーム待ち
        #frames = pipeline.wait_for_frames()
        
        #座標の補正
        #aligned_frames = align.process(frames)
        #color_frame = aligned_frames.get_color_frame()
        #depth_frame = aligned_frames.get_depth_frame()
        #if not depth_frame or not color_frame:
        #    continue

        #RGB_image = np.asanyarray(color_frame.get_data())
        #depth_image = np.asanyarray(depth_frame.get_data())

        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)

        # 表示
        #images = np.hstack((RGB_image, depth_colormap))
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.rectangle(RGB_image, (0, int(size_h - 80)), (size_w, int(size_h - 40)), (0, 255, 0), 2)
        #cv2.rectangle(RGB_image, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
        #cv2.imshow('RealSense', RGB_image)
        
        
        #ret,frame2 = cap.read()
        #cv2.rectangle(frame2, (0, 470), (size_w, 510), (0, 255, 0), 2)
        #cv2.imshow('frame',frame2)

        #img1 = RGB_image
        #img2 = frame2
        

        k=cv2.waitKey(1)
        
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            GPIO.cleanup()
            pipeline.stop()
            break
        if k==ord('s'):#sを押すとスタート
            ball_2 = True
            
            #dist = depth_frame.get_distance(center_x, center_y)
            #print(dist)
            

        if ball_1 == True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()   
            cv2.rectangle(RGB_image, (0, int(size_h - 80)), (size_w, int(size_h - 40)), (0, 255, 0), 2)
            cv2.rectangle(RGB_image, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.imshow('RealSense', RGB_image)     
            img1 = RGB_image


            upper_leht_1_x,upper_leht_1_y,center_ball_1_x,center_ball_1_y,img1 = M_ball.ball_detect(img1)
            #cv2.imshow('RealSense', img1)

            if center_ball_1_x == None:
                #ボール未検出
                #ball_1 = False
                #ball_2 = True
                right_rotation()
                print("未検出")
                pass
            elif center_ball_1_x < (size_w / 2) - 20:                    
                left_rotation() #左回転
                print('left')
            elif center_ball_1_x > (size_w / 2) + 20:                    
                right_rotation() #右回転
                print('right')
            elif (size_w / 2) - 20 <= center_ball_1_x <= (size_w / 2) + 20:
                if center_ball_1_y == None:
                    ball_1 = False
                    ball_2 = True
                    print("未検出")
                    #ボール未検出
                    pass
                elif center_ball_1_y > size_h - 40:
                    down() #後転
                    print('down')
                elif center_ball_1_y < size_h - 80:                        
                    move() #正転
                    print('move')
                elif size_h - 80 <= center_ball_1_y <= size_h - 40:
                    #範囲に入ったら停止
                    print('stop')
                    ball_1 = False
                    ball_2 = True
                else:
                    pass


        if ball_2 == True:
            ret,frame2 = cap.read()

            img2 = frame2

            upper_left_2_x,upper_left_2_y,center_ball_2_x,center_ball_2_y,img2 = M_ball.ball_detect(img2)

            cv2.rectangle(frame2, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.rectangle(frame2, (0, 470), (size_w, 510), (0, 255, 0), 2)
            cv2.imshow('frame', img2)

            print(center_ball_2_x)

            if center_ball_2_x == None:
                #ボール未検出
                #right_rotation()
                ball_1 = True
                ball_2 = False
                print("未検出")
                pass
            elif center_ball_2_x < (size_w / 2) -20:                    
                left_rotation(10) #左回転
                print('left2')
            elif center_ball_2_x > (size_w / 2) +20:                    
                right_rotation(10) #右回転
                print('right2')
            elif (size_w / 2) - 20 <= center_ball_2_x <= (size_w / 2) + 20:
                if upper_left_2_y == None:
                    #ボール未検出,後退
                    down()
                    pass
                elif upper_left_2_y > 490:
                    down() #後転
                    print('down2')
                elif upper_left_2_y < 490:                        
                    move(30) #正転
                    print('move2')
                elif 470 <= upper_left_2_y <= 510:
                    #範囲に入ったら停止
                    print('stop2')
                    ball_1 = False
                    ball_2 = False
                    hole = True
                    p1.ChangeDutyCycle(0)
                    p2.ChangeDutyCycle(0)
                    p3.ChangeDutyCycle(0)
                    p4.ChangeDutyCycle(0)
                else:
                    pass

            for i in range(5):
                cap.read()
            
            
        if hole == True:
	
            print("打球")

            hole = False
            ball_1 = True

            
              
except KeyboardInterrupt:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
