import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import numpy as np
import cv2
import RPi.GPIO as GPIO
import pyrealsense2.pyrealsense2 as rs
import time
import M_ball
import M_flag
import club
import HC_SR04


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


def move(duty):
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    


def down(duty):
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)



def right_rotation(duty):
    #前進
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)

def right_rotation_flag(duty):
    #前進
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    
    

def left_rotation(duty):
    #
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)

def left_rotation_flag(duty):
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
    
GPIO.cleanup()

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
flag = False
cont = False #ボール微調整
hole = False #打球

#画面サイズ設定
size_w = 1280
size_h = 720

#ボール検出範囲設定
x1 = 400
x2 = 590
x3 = 670
x4 = 880

y1 = 360
y2 = 470
y3 = 490
y4 = 510

duty_slow = 10
duty_fast = 30
duty_rotation = 20

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

# club
club_ = club.club()
club_.now_pull_dis = HC_SR04.get_distance(club_.TRIG_PIN, club_.ECHO_PIN, num=5, temp=20)
club_.sheer_down(30)
time.sleep(1)
club_.DC_motor.stop()

club_.sheer_hold()
club_.sheer_move(100, club_.duty)

try:
    while True:
        
        k=cv2.waitKey(1)
        
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            club_.sheer_release()
            club_.end()
            GPIO.cleanup()
            pipeline.stop()
            break

#ボール検出、追尾------------------------------------

        if ball_1 == True:

            ret,frame_ball_1 = cap.read()

            upper_left_1_x,upper_left_1_y,center_ball_1_x,center_ball_1_y,frame_ball_1 = M_ball.ball_detect(frame_ball_1)

            cv2.rectangle(frame_ball_1, (x2, 0), (x3, size_h), (0, 255, 0), 2)
            cv2.rectangle(frame_ball_1, (x1, 0), (x4, size_h), (0, 255, 0), 2)
            cv2.rectangle(frame_ball_1, (0, 470), (size_w, 510), (0, 255, 0), 2)
            cv2.imshow('frame', frame_ball_1)

            print(center_ball_1_x, upper_left_1_y)

            if upper_left_1_x == None:
                right_rotation_flag(duty_rotation)
                print("未検出")
            else:
                if center_ball_1_x < x1 and upper_left_1_y < y1:
                    left_rotation(duty_rotation)
                    print('left')

                if x1 <= center_ball_1_x and center_ball_1_x < x2:
                    if y3 <= upper_left_1_y:
                        down(duty_fast)
                        print('down')
                    else:
                        left_rotation(duty_rotation)
                        print('left')

                if x3 < center_ball_1_x and center_ball_1_x <= x4:
                    if y3 <= upper_left_1_y:
                        down(duty_fast)
                        print('down')
                    else:
                        right_rotation(duty_rotation)
                        print('right')

                if x4 < center_ball_1_x and upper_left_1_y < y1:
                    right_rotation(duty_rotation)
                    print('right')
                

                if x2 <= center_ball_1_x and center_ball_1_x <= x3:
                    if upper_left_1_y < y1:
                        move(duty_fast)
                        print('move fast')
                    else:
                        move(duty_slow)
                        print('move')

                if x4 < center_ball_1_x and y1 <= upper_left_1_y:
                    down(duty_fast)
                    print('down')

                if center_ball_1_x < x1 and y1 <= upper_left_1_y:
                    down(duty_fast)  
                    print('down')

                if x2 <= center_ball_1_x and center_ball_1_x <= x3:
                    if y2 <= upper_left_1_y and upper_left_1_y <= y4:
                        stop()
                        print('stop')
                        ball_1 = False
                        flag = True
                        cv2.destroyWindow('frame')
                        time.sleep(0.1)

            #カメラ処理遅れ対策
            for i in range(5):
                cap.read()



            

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
                left_rotation(50)
                print("未検出2")
            elif center_ball_2_x < (size_w / 2) - 20:                    
                left_rotation(30) #左回転
                print('left2')
            elif center_ball_2_x > (size_w / 2) + 20:                    
                right_rotation(30) #右回転
                print('right2')
            elif (size_w / 2) - 40 <= center_ball_2_x <= (size_w / 2) + 40:
                print('stop2')
                ball_2 = False
                ball_1 = True
                stop()
                cv2.destroyWindow('Realsense')
                time.sleep(0.1)
            else:
                pass
#--------------------------------------------------------------------
            
#フラッグ検出-------------------------------------------------------
        if flag == True:

            x2_f = 620
            x3_f = 660

            frames_flag = pipeline.wait_for_frames()

            #座標の補正
            aligned_frames = align.process(frames_flag)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()
            if not depth_frame or not color_frame:
                continue

            RGB_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            flag_x, center_flag_x, center_flag_y, flag_w, RGB_image = M_flag.flag_detect(RGB_image)

            # 表示
            if center_flag_x != None:
                cv2.rectangle(RGB_image, (x2_f, 0), (x3_f, size_w), (0, 255, 0), 2)
                cv2.imshow('RealSense', RGB_image)
            

            if center_flag_x == None:
                #フラッグ未検出
                right_rotation_flag(40)
                print("未検出")
            else:
                if center_flag_x < x2_f:
                    left_rotation_flag(duty_slow)
                    print('left flag slow')
                if x3_f < center_flag_x:
                    right_rotation_flag(duty_slow) 
                    print('right slow')
                if x2_f <= center_flag_x and center_flag_x <= x3_f:
                #停止
                    print('stop flag')

                    dist_depth = distance(center_flag_x,center_flag_y)
                    if dist_depth == None:
                        #ゼロ除算に引っかかったらもう一回
                        dist_depth = distance(center_flag_x,center_flag_y)

                    flag = False
                    hole = True
                    cv2.destroyWindow('RealSense')
                    time.sleep(0.1)
#------------------------------------------------------------------


#打球位置微調整--------------------------------------------------
        # if cont == True:
        #     #下カメラでボール検出
        #     ret,frame_cont = cap.read()

        #     upper_cont_x,upper_cont_y,center_cont_x,center_cont_y,frame_cont = M_ball.ball_detect(frame_cont)

        #     cv2.rectangle(frame_cont, (int((size_w / 2) - 20), 0), (int((size_w / 2) + 20), size_h), (0, 255, 0), 2)
        #     cv2.rectangle(frame_cont, (0, 470), (size_w, 510), (0, 255, 0), 2)
        #     cv2.imshow('frame_cont', frame_cont)

        #     #回転が必要かは検討
        #     if upper_cont_y == None:
        #         #ボール未検出
        #         down(10)
        #         pass
        #     elif upper_cont_y > point:
        #         down(10) #後転
        #         print('down_cont')
        #     elif upper_cont_y < point:
        #         move(10) #正転
        #         print('move_cont')
        #     elif point - 20 <= upper_cont_y <= point + 20:
        #         #停止
        #         stop()
        #         print('stop_cont')
        #         cont = False
        #         hole = True
        #         cv2.destroyWindow('frame_cont')
        #         time.sleep(0.1)
        #     else:
        #         pass

        #     #カメラ処理遅れ対策
        #     for i in range(5):
        #         cap.read()
#-------------------------------------------------------------

#打球---------------------------------------------------------
        if hole == True:
	
            print(dist_depth)
            #どのタイミングでフラッグの距離計測するか
           
            print("打球")
            club_.sheer_release()

            stop()

            time.sleep(7)

            club_.sheer_hold()
            club_.sheer_move(100, club_.duty)

            hole = False
            ball_1 = True
#-------------------------------------------------------------

            
              
except KeyboardInterrupt:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()
    club_.sheer_release()
    club_.end()
    GPIO.cleanup()
    cap.release()
