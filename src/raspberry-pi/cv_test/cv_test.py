import cv2
import numpy as np
import serial

ser = serial.Serial('/dev/ttyACM0', 9600)

# カメラの設定
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 赤い色の範囲を指定
lower_red1 = np.array([0, 128, 0])
upper_red1 = np.array([13, 255, 255])
lower_red2= np.array([167, 128, 0])
upper_red2 = np.array([179, 255, 255])

# 青色の範囲を指定
lower_blue = np.array([100, 128, 0])
upper_blue = np.array([137, 255, 255])

# 黄色の範囲を指定
lower_yellow = np.array([20, 128, 0])
upper_yellow = np.array([35, 255, 255])

#球の半径[mm]
RADIUS = 32.5


def GetSphere(frame):
    # 画像をHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 赤,青,黄色の範囲内の領域を抽出(二値化)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    count = 0
    for mask in(mask_red, mask_blue, mask_yellow):
        # メディアンフィルタを適用する。
        mask = cv2.medianBlur(mask, ksize=7)
        # 輪郭検出
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            # 輪郭を近似する
            approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True),True)

            # 近似された輪郭が球体に近いかどうかを判断する
            if len(approx) > 12:
                (x,y),radius = cv2.minEnclosingCircle(approx)
                center = (int(x),int(y))
                radius = int(radius)
                if radius > 60:
                    count += 1
                    cv2.circle(frame,center,radius,(0,255,0),2)
                    dis = CalcDistance(radius)
                    # 送信
                    m = str(center[0]) + "," + str(center[1]) + "," + str(dis) + "\n";
                    ser.write(m.encode('utf-8'))
                    # 球体の座標を出力
                    print("球体の座標: ({}, {}), 球体の半径: {}, 距離: {}".format(center[0], center[1], radius, dis))
    cv2.putText(frame, "count:"+str(count), (30,30), 1, 1.5, (255,0,0),2)
    return frame

def CalcDistance(r):
    dis = 0
    fy = 957.51116557
    camy = 2.7
    # camx = 3.6
    #camx, camyはhttp://zattouka.net/GarageHouse/micon/Camera/JPEG/VC0706_1.htmlを参照
    pxl=960
    r = r * camy / pxl
    fy = fy * camy / pxl
    dis = RADIUS *  fy / r
    return dis

if __name__ == "__main__":
    while True:
        # フレームをキャプチャ
        ret, frame = cap.read()
        # 色検出+輪郭検出
        color_contour_frame = GetSphere(frame)
        # 画面に表示
        cv2.imshow('frame(color_contour)',color_contour_frame)

        # ESCキーで終了
        if cv2.waitKey(1) == 27:
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()
