import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import numpy as np
import cv2
import RPi.GPIO as GPIO
import pyrealsense2.pyrealsense2 as rs
import time
import M_ball
import M_flag
import M_bunker

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

    try:
        #ゼロ除算の対策
        dist_mean = sum(dist_new)/len(dist_new)
    except ZeroDivisionError:
        dist_mean = None

    return dist_mean


def right_rotation(duty):
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    


def left_rotation(duty):
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)



def move(duty):
    #前進
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    
    

def down(duty):
    #
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

PIN1 = 6
PIN2 = 13
PIN3 = 5
PIN4 = 0
    

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
            
p1.start(0) 
p2.start(0) 
p3.start(0) 
p4.start(0) 

#------------------------

#フラグの設定
ball_1 = True #下カメラ
ball_2 = False #ボール位置へ移動 デプスカメラ
bunker = False
cont = False #ボール微調整
hole = False #打球

#画面サイズ設定
size_w = 1280
size_h = 720

#下カメラの条件
point = 490


#カメラ設定----------------------------
cap = cv2.VideoCapture(6)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_h)
#--------------------------------------



# ストリーム(Color/Depth)の設定----------
config = rs.config()

config.enable_stream(rs.stream.color, size_w, size_h, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, size_w, size_h, rs.format.z16, 30)

# ストリーミング開始
pipeline = rs.pipeline()
profile = pipeline.start(config)

# Alignオブジェクト生成
align_to = rs.stream.color
align = rs.align(align_to)
#---------------------------------------


try:
    while True:

        k=cv2.waitKey(1)
        
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            GPIO.cleanup()
            pipeline.stop()
            break

#ボール検出、追尾------------------------------------
        if ball_1 == True:
            ret,frame = cap.read()

            bunker_x,bunker_y,bunker_w,bunker_h,bunker_cnt,mask = M_bunker.bunker_detect(frame)
            #upper_left_1_x,upper_left_1_y,center_ball_1_x,center_ball_1_y,frame = M_ball.ball_detect(frame)
            
            cv2.rectangle(frame, (int((size_w / 2) - 100), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.rectangle(frame, (0, 470), (size_w, 510), (0, 255, 0), 2)
            cv2.imshow('frame', frame)
            cv2.imshow('mask',mask)

            print('move')
            move(10)



            if bunker_cnt == None:
                pass
            elif bunker_cnt == 1:
                bunker_MAX = bunker_x[0] + bunker_w[0]
                bunker_min = bunker_y[0]
                bunker = True
                ball_1 = False
                stop()
            elif bunker_cnt == 2:
                #2つバンカーを検出したとき、下にある方を見る
                bunker_y_index = bunker_y.index(max(bunker_y))
                bunker_MAX = bunker_x[bunker_y_index] + bunker_w[bunker_y_index]
                bunker_min = bunker_y[bunker_y_index]
                bunker = True
                ball_1 = False
                stop()
            else:
                pass


            
            
            #カメラ処理遅れ対策
            for i in range(5):
                cap.read()

#---------------------------------------------------------

#バンカー回避----------------------------------------------
        if bunker == True:
            if bunker_min == 0 & bunker_MAX == int(size_w * 0.7):#画面の70％
                #画面いっぱいにバンカーがある
                print('bunker')
                left_rotation(20)
                time.sleep(0.05)
                move(30)
                time.sleep(0.1)
                stop()
                ball_1 = True
                bunker = False
            elif bunker_min == 0 & bunker_MAX < int(size_w * 0.7):
                #画面の左側
                print('bunker r')
                right_rotation(20) 
                time.sleep(0.05)
                move(30)
                time.sleep(0.1)
                stop()
                ball_1 = True
                bunker = False
            elif 0 < bunker_min & bunker_MAX == size_w:
                #画面の右側
                print('bunker l')
                left_rotation(20)
                time.sleep(0.05)
                move(30)
                time.sleep(0.1)
                ball_1 = True
                bunker = False
            else:
                pass
#--------------------------------------------------------




#下カメラでボール未検出------------------------------------
        if ball_2 == True:
            #デプスカメラ
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()   
                 
            upper_left_2_x,upper_left_2_y,center_ball_2_x,center_ball_2_y,color_frame = M_ball.ball_detect(color_frame)

            cv2.rectangle(color_frame, (0, int(size_h - 80)), (size_w, int(size_h - 40)), (0, 255, 0), 2)
            cv2.rectangle(color_frame, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.imshow('RealSense', color_frame)

            if center_ball_2_x == None:
                #ボール未検出
                left_rotation(10)
                print("未検出2")
                pass
            elif center_ball_2_x < (size_w / 2) - 20:                    
                left_rotation(10) #左回転
                print('left2')
            elif center_ball_2_x > (size_w / 2) + 20:                    
                right_rotation(10) #右回転
                print('right2')
            elif (size_w / 2) - 20 <= center_ball_2_x <= (size_w / 2) + 20:
                if center_ball_2_y == None:
                    left_rotation()
                    print("未検出2")
                    #ボール未検出
                    pass
                elif center_ball_2_y > size_h - 40:
                    down(30) #後転
                    print('down2')
                elif center_ball_2_y < size_h - 80:                        
                    move(30) #正転
                    print('move2')
                elif size_h - 80 <= center_ball_2_y <= size_h - 40:
                    #範囲に入ったら停止
                    print('stop2')
                    ball_2 = False
                    ball_1 = True
                    stop()
                else:
                    pass
#--------------------------------------------------------------------



#打球---------------------------------------------------------
        if hole == True:

            #どのタイミングでフラッグの距離計測するか
            #dist_depth = distance(center_flag_x,center_flag_y)
            #if dist_depth == None:
                #ゼロ除算に引っかかったらもう一回
             #   dist_depth = distance(center_flag_x,center_flag_y)

            print("打球")

            hole = False
            #ball_1 = True
#-------------------------------------------------------------

            
              
except KeyboardInterrupt:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
