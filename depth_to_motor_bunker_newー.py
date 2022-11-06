import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import RPi.GPIO as GPIO
import sys
import numpy as np
import pyrealsense2 as rs
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
    dist1 = depth_frame.get_distance(center_x, center_y)
    dist2 = depth_frame.get_distance(center_x + 5, center_y + 5)
    dist3 = depth_frame.get_distance(center_x + 5, center_y - 5)
    dist4 = depth_frame.get_distance(center_x - 5, center_y + 5)
    dist5 = depth_frame.get_distance(center_x - 5, center_y - 5)

    dist.extend(format(dist1,'.4f'),format(dist2,'.4f'),format(dist3,'.4f'),format(dist4,'.4f'),format(dist5,'.4f'))
    #3.5m以上の点は除外して平均
    dist_new = [i for i in dist if i < 3.5]
    dist_mean = sum(dist_new)/len(dist_new)

    return dist_mean


def left_rotation():
    #左回転(左が後転、右が正転)
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    time.sleep(10)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(10)


def right_rotation():
    #右回転(左が正転、右が後転)
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    time.sleep(10)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(10)


def move():
    #正転
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(duty)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(duty)
    time.sleep(10)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(10)
    

def down():
    #後転
    p1.ChangeDutyCycle(duty)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(duty)
    p4.ChangeDutyCycle(0)
    time.sleep(10)
    #停止
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)
    p3.ChangeDutyCycle(0)
    p4.ChangeDutyCycle(0)
    time.sleep(10)





if __name__ == '__main__':

    #カメラ設定----------------------------
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    print("Camera start")
    #--------------------------------------

    #realsense設定-------------------------
    # ストリーム(Color/Depth)の設定
    config = rs.config()

    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

    # ストリーミング開始
    pipeline = rs.pipeline()
    profile = pipeline.start(config)
    #---------------------------------------

    #GPIO初期設定------------
    GPIO.setmode(GPIO.BCM)

    PIN1 = 17
    PIN2 = 22
    PIN3 = 27
    PIN4 = 18
    #sw_PIN = 15


    GPIO.setup(PIN1, GPIO.OUT)
    GPIO.setup(PIN2, GPIO.OUT)
    GPIO.setup(PIN3, GPIO.OUT)
    GPIO.setup(PIN4, GPIO.OUT)
    #GPIO.setup(sw_PIN, GPIO.IN)

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
    ball_1 = False #ボール位置へ移動 デプスカメラ
    ball_1_bunker = False #ボール位置へ移動　デプスカメラ　バンカーあり
    ball_2 = False #下カメラ
    sense = False #realsense距離計測
    flag = False #フラッグ検出
    cont = False #ボール微調整
    depth = False #距離計測
    hole = False #打球
    bunker = False #バンカー検出

#GUIかなにかでボタン押したらスタートできるように(ball=True)
#キーボードでも可


    try:
        while True:
            frame1 = pipeline.wait_for_frames()

            #RGB
            RGB_frame = frame1.get_color_frame()
            RGB_image = np.asanyarray(RGB_frame.get_data())

            #depyh
            depth_frame = frame1.get_depth_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)

            ret,frame2 = cap.read()
            cv2.imshow('frame',frame2)

            img1 = RGB_image
            img2 = frame2

            #ボタンが押されたらスタート
            #sw = GPIO.input(sw_PIN) 
            #if sw == 0:#スイッチが押されたらスタート
                #ball_1 = True
                #ball_1_bunker = True

            c = cv2.waitKey(1)
            if c == ord('s'):
                ball_1 = True
                ball_1_bunker = True
            if c == ord('q'):
                cv2.destroyAllWindows()
                cap.release()
                pipeline.stop()
                GPIO.cleanup()
                break


        # ボール位置へ移動------------------------------------------
            if ball_1 == True:

                center_ball_1_x,center_ball_1_y = M_ball.ball_detect(img1)

                if center_ball_1_x == None:
                    #ボール未検出
                    ball_2 = True
                    pass
                elif center_ball_1_x < 620:                    
                    left_rotation() #左回転
                elif center_ball_1_x > 660:                    
                    right_rotation() #右回転
                elif 620 <= center_ball_1_x <= 660:
                    if center_ball_1_y == None:
                    #ボール未検出
                        pass
                    elif center_ball_1_y < 360:
                        down() #後転
                    elif center_ball_1_y > 360:                        
                        move() #正転
                    elif 320 <= center_ball_1_y <= 380:
                        #範囲に入ったら停止
                        ball_1 = False
                        ball_1_bunker = False
                        flag = True
                else:
                    pass
        #---------------------------------------------------


        #バンカー検出------------------------------------
            if ball_1_bunker == True:

                x,y,w,h,center_bunker_x,center_bunker_y = M_bunker.bunker_detect(img1)

                #2つのバンカー領域のうち左を1，右を2とする
                #バンカー領域1つしか検出していない時

                if len(x) == 1:
                    bunker_x = x[0] + (w[0] / 2)
                    bunker_y = y[0] + h[0]
                    dist_bunker_sense1 = distance(bunker_x, bunker_y)
 
                    if dist_bunker_sense1 < 0.15:
                        bunker_choice = 1
                        bunker = True
                elif len(x) == 2:
                    bunker1_sense_index = x.index(min(x))

                    if bunker1_sense_index == 0:
                        bunker2_sense_index = 1
                    else:
                        bunker2_sense_index = 0

                    bunker1_x = x[bunker1_sense_index] + (w[bunker1_sense_index] / 2)
                    bunker1_y = y[bunker1_sense_index] + h[bunker1_sense_index]
                    dist_bunker_sense1 = distance(bunker1_x, bunker1_y)
                    bunker_choice = 1

                    bunker2_x = x[bunker2_sense_index] + (w[bunker2_sense_index] / 2)
                    bunker2_y = y[bunker2_sense_index] + h[bunker2_sense_index]
                    dist_bunker_sense2 = distance(bunker2_x, bunker2_y)

                    if dist_bunker_sense1 < 0.15:
                        bunker_choice = 1
                        bunker = True
                        ball_1 = False
                    if dist_bunker_sense2 < 0.15:
                        #バンカーとの距離が50cm以内
                        bunker_choice = 2
                        bunker = True
                        ball_1 = False
                else:
                    pass
        #--------------------------------------------------


        #バンカー避け---------------------------------------
            if bunker == True:
                if bunker_choice == 1:
                    right_rotation()
                    time.sleep(1)
                    move()
                    time.sleep(1)
                if bunker_choice == 2:
                    left_rotation()
                    time.sleep(1)
                    move()
                    time.sleep(1)

                ball_1 = True
                ball_1_bunker = True

        #--------------------------------------------------




        #ボール探索(下カメラ)--------------------------------
            if ball_2 == True:
                center_ball_x,center_ball_y = M_ball.ball_detect(img2)

                if center_ball_x == None:
                    #ボール未検出
                    pass
                elif center_ball_x < 620:
                    left_rotation() #左回転
                elif center_ball_x > 660:                   
                    right_rotation() #右回転
                elif 620 <= center_ball_x <= 660:
                    if center_cont_y == None:
                        #ボール未検出
                        pass
                    elif center_cont_y < 360:
                        down() #後転
                    elif center_cont_y > 360:                        
                        move() #正転
                    elif 320 <= center_cont_y <= 380:
                        #範囲に入ったら停止
                        pass

                    flag = True
                    ball_1 = False
                    ball_2 = False
                else:
                    pass
        #---------------------------------------------------



        # フラッグ検出---------------------------------------        
            if flag == True:
                center_flag_x,center_flag_y = M_flag.flag_detect(img1)

                if center_flag_x == None:
                    #フラッグ未検出
                    pass
                elif center_flag_x < 620:
                    left_rotation() #左回転
                elif center_flag_x > 660:
                    right_rotation() #右回転
                elif 620 <= center_flag_x <= 660:
                    #停止
                    flag = False
                    cont = True
                else:
                    pass

                pass
        #---------------------------------------------------


        #ボール位置の微調整----------------------------------
            if cont == True:
                #下カメラでボール検出
                #以下のcenterは下カメラ
                center_cont_x,center_cont_y = M_ball.ball_detect(img2)

                if center_cont_x == None:
                    #ボール未検出
                    pass
                elif center_cont_x < 360:
                    down() #後転
                elif center_cont_x > 360:
                    move() #正転
                elif 320 <= center_cont_x <= 380:
                    #停止
                    cont = False
                    depth = True
                else:
                    pass
        #---------------------------------------------------


        #距離計測--------------------------------------------
            if depth == True:
                center_depth_x,center_depth_y = M_flag.flag_detect(img1)

                dist_depth = distance(center_depth_x, center_depth_y)

                depth = False
                hole = True
                
        #---------------------------------------------------


        #打球-----------------------------------------------
            if hole == True:


                hole = False
                ball = True
                pass
        #---------------------------------------------------
            


    except KeyboardInterrupt:
        pass

    GPIO.cleanup()
    cap.release()
    pipeline.stop()
    cv2.destroyAllWindows()
    