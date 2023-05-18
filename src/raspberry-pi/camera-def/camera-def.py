import cv2
import numpy as np

"""
グローバル宣言

lower_red1, upper_red1 : 赤色の範囲その1
lower_red2, upper_red2 : 赤色の範囲その2
lower_blue, upper_blue : 青色の範囲
lower_yellow, upper_yellow : 黄色の範囲
RADIUS : 球の半径
WIDTH : 取得画像の横の解像度
HEIGHT : 取得画像の縦の解像度
SPHERE_VERTEX : 球とみなす頂点数
SPHERE_MAX_DIS : 球とみなす最大の距離
"""

# 赤い色の範囲を指定
lower_red1 = np.array([0, 128, 0])
upper_red1 = np.array([10, 255, 255])
lower_red2= np.array([167, 128, 0])
upper_red2 = np.array([179, 255, 255])

# 青色の範囲を指定
lower_blue = np.array([90, 128, 0])
upper_blue = np.array([137, 255, 255])

# 黄色の範囲を指定
lower_yellow = np.array([15, 64, 0])
upper_yellow = np.array([35, 255, 255])

# 球の半径[mm]
RADIUS = 32.5

# 取得画像の解像度
WIDTH = 640
HEIGHT = 480

# 球とみなす頂点数
SPHERE_VERTEX = 12

# 球とみなす最大の距離
SPHERE_MAX_DIS = 1000

def SetCamera(width, height):
    """
    Webカメラとcv2を使う準備

    Parameters
    ----------
    width : 取得画像の横の解像度
    height : 取得画像の縦の解像度

    Returns
    -------
    cap : cv2のビデオキャプチャ
    """
    # カメラの設定
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


def FindTarget(frame):
    """
    一番近い球の座標，距離，色を取得する

    Parameters
    ----------
    frame : 取得画像

    Returns
    -------
    x[col] : 球の中心のx座標(ピクセル)
    y[col] : 球の中心のy座標(ピクセル)
    dis[col] : 球までの距離[mm](キャリブレーションを用いた値を使用するためズレがある)
    col : 球の色(0:赤, 1:青, 2:黄)
    """
    x=np.zeros(3)
    y=np.zeros(3)
    dis=np.zeros(3)
    r=np.zeros(3)

    # 二値画像の取得
    (mask_red, mask_blue, mask_yellow) = Masking(frame)
    
    for i, mask in enumerate([mask_red, mask_blue, mask_yellow]):
        # メディアンフィルタを適用する。
        mask = cv2.medianBlur(mask, ksize=7)

        # 色ごとに，最も近い球の座標と距離(とデバッグ用の半径)を取得
        x[i], y[i], dis[i], r[i] = GetCoordinatesAndDistance(mask)
        # cv2.circle(mask,(int(x[i]),int(y[i])),int(r[i]),(0,255,0),2)   デバッグ用　画面に円を表示する準備
    # cv2.imshow("mask", mask_red + mask_blue + mask_yellow)   デバッグ用　画面にマスク表示

    # 最も近い球の色を取得する
    col = np.argmin(dis)
    return x[col], y[col], dis[col], col

def Masking(frame):
    """
    赤，青，黄でマスキングして二値画像を取得する

    Parameters
    ----------
    frame : 取得画像

    Returns
    -------
    (mask_red, mask_blue, mask_yellow) : (赤の二値画像, 青の二値画像, 黄の二値画像)
    """

    # 画像をHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 赤,青,黄色の範囲内の領域を抽出(二値化)
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    return (mask_red, mask_blue, mask_yellow)

def GetCoordinatesAndDistance(mask):
    """
    二値画像から，距離が最も近い球の座標と距離を取得する

    Parameters
    ----------
    mask : 二値画像

    Returns
    (min_x, min_y, min_dis, min_r) : (最も近い球のx座標, 最も近い球のy座標, 最も近い距離, 最も近い球の半径(デバッグ用))
    -------
    
    """
    min_x = 0
    min_y = 0
    min_dis = SPHERE_MAX_DIS
    min_r = 0

    # 輪郭検出
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # 輪郭を近似する
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True),True)

        # 近似された輪郭が球体に近いかどうかを判断する
        if len(approx) > SPHERE_VERTEX:
            (x,y),r = cv2.minEnclosingCircle(cnt)
            dis = CalcDistance(r)
            # 最小値なら入れ替え
            if dis<min_dis:
                min_x = int(x)
                min_y = int(y)
                min_dis = int(dis)
                min_r = int(r)
    return (min_x, min_y, min_dis, min_r)

def CalcDistance(r):
    """
    球の半径から距離を計算する

    Parameters
    ----------
    r : 球の半径

    Returns
    -------
    dis : カメラから球までの距離[mm](キャリブレーションを用いた値を使用するためズレがある)
    """
    dis = 0
    fy = 957.51116557
    camy = 2.4
    pxl = HEIGHT
    r = r * camy / pxl
    fy = fy * camy / pxl
    dis = RADIUS *  fy / r
    return dis

if __name__ == "__main__":
    # 使用例
    cap = SetCamera(WIDTH, HEIGHT)
    while True:
        # フレームをキャプチャ
        ret, frame = cap.read()
        # 色検出+輪郭検出
        x, y, dis, col = FindTarget(frame)

        # デバッグ
        print(x, y, dis, col)

        # ESCキーで終了
        if cv2.waitKey(1) == 27:
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()
