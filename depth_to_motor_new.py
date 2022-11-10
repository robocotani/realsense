import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import numpy as np
import cv2
import RPi.GPIO as GPIO
import pyrealsense2.pyrealsense2 as rs
import time
import M_ball
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
    
    #0.1m以下、3.5m以上の点は除外して平均
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

PIN1 = 13
PIN2 = 6
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
cont = False #ボール微調整
depth = False #距離計測
hole = False #打球

#画面サイズ設定
size_w = 1280
size_h = 720

#下カメラの条件
point = 490


#カメラ設定----------------------------
cap = cv2.VideoCapture(0)
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

            upper_left_1_x,upper_left_1_y,center_ball_1_x,center_ball_1_y,frame = M_ball.ball_detect(frame)

            cv2.rectangle(frame, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.rectangle(frame, (0, 470), (size_w, 510), (0, 255, 0), 2)
            cv2.imshow('frame', frame)

            if center_ball_1_x == None:
                #ボール未検出
                ball_2 = True
                ball_1 = False
                print("未検出")
                pass
            elif center_ball_1_x < (size_w / 2) - 20:                    
                left_rotation(10) #左回転
                print('left')
            elif center_ball_1_x > (size_w / 2) + 20:                    
                right_rotation(10) #右回転
                print('right')
            elif (size_w / 2) - 20 <= center_ball_1_x <= (size_w / 2) + 20:
                if upper_left_1_y == None:
                    #ボール未検出,後退
                    down(30)
                    pass
                elif upper_left_1_y > point:
                    down(30) #後転
                    print('down')
                elif upper_left_1_y < point:                        
                    move(30) #正転
                    print('move')
                elif point - 20 <= upper_left_1_y <= point + 20:
                    #範囲に入ったら停止
                    print('stop')
                    ball_1 = False
                    ball_2 = False
                    hole = True
                    stop()
                else:
                    pass
            
            #カメラ処理遅れ対策
            for i in range(5):
                cap.read()

#---------------------------------------------------------

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
            
#フラッグ検出-------------------------------------------------------
        if flag == True:

            frames = pipeline.wait_for_frames()

            #座標の補正
            aligned_frames = align.process(frames)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            if not depth_frame or not color_frame:
                continue

            RGB_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            center_flag_x,center_flag_y,RGB_image = M_flag.flag_detect(RGB_image)

            # 表示
            cv2.rectangle(RGB_image, ((size_w / 2) - 20, 0), ((size_w / 2) + 20, size_w), (0, 255, 0), 2)
            cv2.imshow('RealSense', RGB_image)

            if center_flag_x == None:
                #フラッグ未検出
                print("未検出")
                pass
            elif center_flag_x < (size_w / 2) - 20:
                left_rotation(10) #左回転
                print('left')
            elif center_flag_x > (size_w / 2) + 20:
                right_rotation(10) #右回転
                cv2.circle(RGB_image,(center_flag_x,center_flag_y),2,(0,255,0),3)
                print('right')
            elif (size_w / 2) - 20 <= center_flag_x <= (size_w / 2) + 20:
                #停止
                print('stop')
                flag = False
                cont = True
            else:
                pass
#------------------------------------------------------------------


#打球位置微調整--------------------------------------------------
        if cont == True:
            #下カメラでボール検出
            ret,frame = cap.read()

            upper_left_1_x,upper_left_1_y,center_ball_1_x,center_ball_1_y,frame = M_ball.ball_detect(frame)

            cv2.rectangle(frame, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
            cv2.rectangle(frame, (0, 470), (size_w, 510), (0, 255, 0), 2)
            cv2.imshow('frame', frame)

            #以下のcenterは下カメラ
            center_cont_x,center_cont_y,frame = M_ball.ball_detect(frame)

            #回転が必要かは検討
            if center_cont_x == None:
                #ボール未検出
                down(10)
                pass
            elif center_cont_x < point:
                down(10) #後転
            elif center_cont_x > point:
                move(10) #正転
            elif point - 20 <= center_cont_x <= point + 20:
                #停止
                stop()
                cont = False
                hole = True
            else:
                pass

            #カメラ処理遅れ対策
            for i in range(5):
                cap.read()
#-------------------------------------------------------------

#打球---------------------------------------------------------
        if hole == True:
	
            #どのタイミングでフラッグの距離計測するか
            dist_depth = distance(center_flag_x,center_flag_y)
            if dist_depth == None:
                #ゼロ除算に引っかかったらもう一回
                dist_depth = distance(center_flag_x,center_flag_y)

            print("打球")

            hole = False
            ball_1 = True
#-------------------------------------------------------------

            
              
except KeyboardInterrupt:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()
