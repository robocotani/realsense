import pyrealsense2 as rs
import numpy as np
import cv2


size_w = 1280
size_h = 720


# ストリーム(Color/Depth)の設定
config = rs.config()

config.enable_stream(rs.stream.color, size_w, size_h, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, size_w, size_h, rs.format.z16, 30)

# ストリーミング開始
pipeline = rs.pipeline()
profile = pipeline.start(config)

# Alignオブジェクト生成
align_to = rs.stream.color
align = rs.align(align_to)


try:
    while True:
        # フレーム待ち
        frames = pipeline.wait_for_frames()

        #座標の補正
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        if not depth_frame or not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

         #depth imageをカラーマップに変換
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.08), cv2.COLORMAP_JET)



        # 表示
        images = np.hstack((color_image, depth_colormap))
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)

        k=cv2.waitKey(1)
        if k==ord('q'):#qで終了
            cv2.destroyAllWindows()
            break
        if k==ord('s'):#sを押すと距離と画像を取得
            pass
            dist = depth_frame.get_distance(size_w/2, size_h/2)
            #cv2.putText(RGB_image,format(dist,'.4f'),org=(x+w+20, y+h+20),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,color=(0, 255, 0),thickness=2,lineType=cv2.LINE_4)
            #cv2.imwrite('green/img_4m.jpg',RGB_image)
            print(dist)
            #print(target)

finally:
    # ストリーミング停止
    pipeline.stop()