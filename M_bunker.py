#フラッグが検出されていないときの処理を追加
#ボール以下の面積を除外

import cv2
import numpy as np

def bunker_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # バンカーのHSVの値域1
    hsv_min = np.array([15,0,0])
    hsv_max = np.array([30,255,130])
    mask = cv2.inRange(hsv, hsv_min, hsv_max)

    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)



    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(closing)

    # 特徴抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center_data = np.delete(label[3], 0, 0) #背景の情報削除

    #面積が70以上の領域のデータのみ保存
    l_data = len(data)
    x = []
    y = []
    w = []
    h = []
    area = []
    center_x = []
    center_y = []
    cnt = 0
    for i in range(l_data):
        if 70 <= data[i, 4]:
            x.append(data[i, 0])
            y.append(data[i, 1])
            w.append(data[i, 2])
            h.append(data[i, 3])
            area.append(data[i, 4])
            center_x.append(int(center_data[i][0]))
            center_y.append(int(center_data[i][1]))
            cnt = cnt + 1

    if cnt == 0: #バンカー未検出
        return None,None,None,None,None
        
    return x,y,w,h,cnt

