import cv2
import numpy as np

def red_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 赤色のHSVの値域1
    hsv_min = np.array([0,100,100])
    hsv_max = np.array([15,255,255])
    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)

    # 赤色のHSVの値域2
    hsv_min = np.array([165,100,100])
    hsv_max = np.array([179,255,255])
    mask2 = cv2.inRange(hsv, hsv_min, hsv_max)
    
    return mask1 + mask2


def removenoise(mask_img):
    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(mask_img, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    return closing


# 赤色領域の座標取得
def analysis_blob(binary_img):
    # 2値画像のラベリング処理
    label = cv2.connectedComponentsWithStats(binary_img)

    # 特徴抽出
    n = label[0] - 1
    data = np.delete(label[2], 0, 0)
    center = np.delete(label[3], 0, 0) #背景の情報削除

    #print(data)
    #print(center)

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

# 赤色検出
mask = red_detect(img)

#ノイズ除去
mask_new=removenoise(mask)

# マスク画像を解析
target = analysis_blob(mask_new)

#print(target)

# 中心座標を取得
center_x = int(target["center"][0])
center_y = int(target["center"][1])

# フレームに矩形を描画
x=target["upper_left"][0]
y=target["upper_left"][1]
w=target["width"]
h=target["height"]
cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 10)


 # 結果表示
cv2.imwrite("flag/Frame3.jpg", img)
cv2.imwrite("flag/Mask3.jpg", mask_new)

# qキーが押されたら途中終了
cv2.waitKey(0)
