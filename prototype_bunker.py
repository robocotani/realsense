import cv2
import numpy as np

def green_detect(img):
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # バンカーのHSVの値域1
    hsv_min = np.array([15,0,0])
    hsv_max = np.array([30,255,130])
    mask1 = cv2.inRange(hsv, hsv_min, hsv_max)
    
    return mask1

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
    center = np.delete(label[3], 0, 0) 

    area2=data[(100<data[:,4]) & (data[:,4]<10000)]
    print(area2)

    return area2


img = cv2.imread("sozai/bunker.jpg")
#gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# 赤色検出
mask = green_detect(img)

#ノイズ除去
mask_new=removenoise(mask)

# マスク画像を解析
target = analysis_blob(mask_new)

#print(target)

cnt=len(target)
for i in range(cnt):
    x=target[i][0]
    y=target[i][1]
    w=target[i][2]
    h=target[i][3]
    cv2.rectangle(img, (x,y), (x + w, y + h), (0, 255, 0), 2)

 # 結果表示
cv2.imshow("Frame", img)
cv2.imshow("Mask", mask_new)
cv2.imwrite("bunker/Frame.jpg", img)
cv2.imwrite("bunker/Mask.jpg", mask_new)

# qキーが押されたら途中終了
cv2.waitKey(0)
