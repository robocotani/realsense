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
def analysis_blob_red(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

    # 特徴抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0) #背景の情報削除

    #print(data)
    #print(center)

    return data,center


# ボール領域の座標取得
def analysis_blob_ball(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

    # 特徴抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0) #背景の情報削除

    # 面積最大のインデックス
    max_index = np.argmax(data[:, 4])

    # 情報格納用
    maxblob = {}

    # 各種情報を取得
    maxblob["upper_left"] = (data[:, 0][max_index], data[:, 1][max_index]) # 左上座標
    maxblob["width"] = data[:, 2][max_index]  # 幅
    maxblob["height"] = data[:, 3][max_index]  # 高さ
    maxblob["area"] = data[:, 4][max_index]   # 面積
    maxblob["center"] = center[max_index]  # 中心座標

    return maxblob




img = cv2.imread("sozai/test3.jpg")
#gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#cv2.imshow("Frame", img)

# ボール検出-----------------------------
mask_ball = ball_detect(img)
#ノイズ除去
mask_ball_new=removenoise(mask_ball)
# マスク画像を解析
target_ball= analysis_blob_ball(mask_ball_new)
#--------------------------------------



#ボールの座標取得、矩形描画
x=target_ball["upper_left"][0]
y=target_ball["upper_left"][1]
w=target_ball["width"]
h=target_ball["height"]
center_x = int(target_ball["center"][0])
center_y = int(target_ball["center"][1])
cv2.circle(img,(center_x,center_y),2,(0,0,255),3)
cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 2)
cv2.putText(img,"ball",org=(x + w + 20, y + h + 20),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,color=(0, 255, 0),thickness=2,lineType=cv2.LINE_4)


"""
# 中心座標を取得
center_x = int(center[1][0])
center_y = int(center[1][1])
"""

img1 = cv2.resize(img, dsize=None, fx=0.5, fy=0.5)
mask_b = cv2.resize(mask_ball_new, dsize=None, fx=0.5, fy=0.5)

 # 結果表示
cv2.imwrite("ball/Frame3.jpg", img1)
cv2.imwrite("ball/Mask3.jpg", mask_b)

# qキーが押されたら途中終了
cv2.waitKey(0)
