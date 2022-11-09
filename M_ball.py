
import cv2
import numpy as np


def ball_detect(img):
    #黄色の検出
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ボールのHSVの値域
    hsv_min = np.array([25,100,100])
    hsv_max = np.array([35,255,255])
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

    #面積が30以上の領域のデータのみ保存
    l_data = len(data)
    x = []
    y = []
    w = []
    h = []
    area = []
    center = []
    cnt = 0
    for i in range(l_data):
        if data[i, 4]>=30:
            x.append(data[i, 0])
            y.append(data[i, 1])
            w.append(data[i, 2])
            h.append(data[i, 3])
            area.append(data[i, 4])
            center.append(center_data[i])
            cnt = cnt + 1

    if cnt == 0: #ボール未検出
        return None,None,None,None,None
    elif cnt == 1: #既に最大データのみ(ラベル数が1)
        center_x = int(center[0][0])
        center_y = int(center[0][1])
        cv2.circle(img,(center_x,center_y),2,(0,0,255),3)
        #cv2.rectangle(img, (x[0] ,y[0]), (x[0] + w[0], y[0] + h[0]), (0, 255, 0), 2)
        return x[0],y[0],center_x,center_y,img
    else:
        #最大値を取得
        max_index = np.argmax(area)

        maxblob = {}

        # 各種情報を取得
        maxblob["upper_left"] = (x[max_index], y[max_index]) # 左上座標
        maxblob["width"] = w[max_index]  # 幅
        maxblob["height"] = h[max_index]  # 高さ
        maxblob["area"] = area[max_index]   # 面積
        maxblob["center"] = center[max_index]  # 中心座標

        #ボールの座標取得、矩形描画
        x=maxblob["upper_left"][0]
        y=maxblob["upper_left"][1]
        w=maxblob["width"]
        h=maxblob["height"]
        center_x = int(maxblob["center"][0])
        center_y = int(maxblob["center"][1])
        cv2.circle(img,(center_x,center_y),2,(0,0,255),3)
        #cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 2)
        
    #左上のx座標、横幅、重心
    return x,y,center_x,center_y,img




