#ボールが検出されていないときの処理を追加
#ボール以下の面積を除外


import cv2
import numpy as np

#黄色の検出
def ball_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # ボールのHSVの値域
    hsv_min = np.array([25,100,100])
    hsv_max = np.array([35,255,255])
    mask = cv2.inRange(hsv, hsv_min, hsv_max)
    
    return mask


def removenoise(mask_img):
    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(mask_img, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    return closing


# 領域の座標取得
def analysis_blob_ball(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

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
    cnt=0
    for i in range(l_data):
        if data[i, 4]>=30:
            x.append(data[i, 0])
            y.append(data[i, 1])
            w.append(data[i, 2])
            h.append(data[i, 3])
            area.append(data[i, 4])
            center.append(center_data[i])
            cnt=cnt+1

    return x,y,w,h,area,center,cnt



def max_blob(x,y,w,h,area,center):

    max_index = np.argmax(area)

    maxblob = {}

    # 各種情報を取得
    maxblob["upper_left"] = (x[max_index], y[max_index]) # 左上座標
    maxblob["width"] = w[max_index]  # 幅
    maxblob["height"] = h[max_index]  # 高さ
    maxblob["area"] = area[max_index]   # 面積
    maxblob["center"] = center[max_index]  # 中心座標

    return maxblob



#---main---
img = cv2.imread("green/img_3.5m.jpg")
#img = cv2.imread("green/img_1m.jpg")


# ボール検出-----------------------------
mask_ball = ball_detect(img)
#ノイズ除去
mask_ball_new=removenoise(mask_ball)
# マスク画像を解析
x,y,w,h,area,center,cnt = analysis_blob_ball(mask_ball_new)
#--------------------------------------


if cnt==0: #ボール未検出
    print("ボールが検出できません")
elif cnt==1: #既に最大データのみ(ラベル数が1)
    center_x = int(center[0][0])
    center_y = int(center[0][1])
    cv2.circle(img,(center_x,center_y),2,(0,0,255),3)
    cv2.rectangle(img, (x[0] ,y[0]), (x[0] + w[0], y[0] + h[0]), (0, 255, 0), 2)
    cv2.putText(img,"ball",org=(x[0] + w[0] + 20, y[0] + h[0] + 20),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,color=(0, 255, 0),thickness=2,lineType=cv2.LINE_4)
else:
    #最大値を取得
    target_ball = max_blob(x,y,w,h,area,center)

    #ボールの座標取得、矩形描画
    x=target_ball["upper_left"][0]
    y=target_ball["upper_left"][1]
    w=target_ball["width"]
    h=target_ball["height"]
    center_x = int(center["center"][0])
    center_y = int(center["center"][1])
    cv2.circle(img,(center_x,center_y),2,(0,0,255),3)
    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(img,"ball",org=(x + w + 20, y + h + 20),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,color=(0, 255, 0),thickness=2,lineType=cv2.LINE_4)



#img1 = cv2.resize(img, dsize=None, fx=0.5, fy=0.5)
#mask_b = cv2.resize(mask_ball_new, dsize=None, fx=0.5, fy=0.5)

 # 結果表示
cv2.imshow("ball/Frame_3.5m.jpg", img)
cv2.imshow("ball/Mask_3.5m.jpg", mask_ball_new)

# qキーが押されたら途中終了
cv2.waitKey(0)
