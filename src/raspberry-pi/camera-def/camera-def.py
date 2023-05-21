import cv2
import numpy as np
import time

"""
グローバル宣言
"""

# 赤い色の範囲を指定
lower_red1 = np.array([0, 64, 20])
upper_red1 = np.array([15, 255, 255])
lower_red2= np.array([225, 64, 20])
upper_red2 = np.array([255, 255, 255])

# 青色の範囲を指定
lower_blue = np.array([130, 64, 20])
upper_blue = np.array([175, 255, 255])

# 黄色の範囲を指定
lower_yellow = np.array([20, 64, 20])
upper_yellow = np.array([50, 255, 255])

# 球の半径[mm]
RADIUS = 32.5

# 取得画像の解像度
WIDTH = 320
HEIGHT = 240

# 球とみなす円形度
THRES_CIRCULARITY = 0.75

# 球を検出できる最大の距離
DETECTABLE_MAX_DIS = 1000

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
    dis[col] : 球までの距離[mm](キャリブレーションを用いた値)
    col : 球の色(0:赤, 1:青, 2:黄)
    """
    x = np.zeros(3)
    y = np.zeros(3)
    dis = np.zeros(3)
    r = np.zeros(3)

    # 二値画像の取得
    (mask_red, mask_blue, mask_yellow) = Masking(frame)
    
    for i, mask in enumerate([mask_red, mask_blue, mask_yellow]):
        # メディアンフィルタを適用する。
        mask = cv2.medianBlur(mask, ksize=5)

        # 色ごとに，最も近い球の座標と距離(とデバッグ用の半径)を取得
        x[i], y[i], dis[i], r[i] = GetCoordinatesAndDistance(mask)
        # cv2.circle(frame,(int(x[i]),int(y[i])),int(r[i]),(0,255,0),2)   #デバッグ用　画面に円を表示する準備
    # cv2.imshow("frame", frame)   #デバッグ用　画面に表示
    # cv2.imshow("mask", mask_red + mask_blue + mask_yellow)   #デバッグ用　画面に表示

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
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
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
    (x, y, dis, r) : (最も近い球のx座標, 最も近い球のy座標, 最も近い距離, 最も近い球の半径(デバッグ用))
    -------
    
    """
    # 輪郭検出
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        x = np.zeros(len(contours))
        y = np.zeros(len(contours))
        r = np.zeros(len(contours))
        for i, cnt in enumerate(contours):
            # 輪郭の円形度を計算する
            cir = CalcCircularity(cnt)
            if cir > THRES_CIRCULARITY:
                # 外接円の座標と半径を取得
                (x[i],y[i]),r[i] = cv2.minEnclosingCircle(cnt)
        # 最も半径の大きい球の配列番号を取得
        n = np.argmax(r)
        # 距離を計算
        dis = CalcDistance(r[n])
        return x[n], y[n], dis, r[n]
    else:
        return 0, 0, DETECTABLE_MAX_DIS, 0

def CalcCircularity(cnt):
    '''
    円形度を求める

    Parameters
    ----------
    cnt : 輪郭の(x,y)座標の配列

    Returns
    -------
        円形度

    '''
    # 面積
    area = cv2.contourArea(cnt)
    # 周囲長
    length = cv2.arcLength(cnt, True)
    # 円形度を求める
    try:
        cir = 4*np.pi*area/length/length
    except ZeroDivisionError:
        cir = 0
    return cir

def CalcDistance(r):
    """
    球の半径から距離を計算する

    Parameters
    ----------
    r : フレーム中の球の半径(ピクセル)

    Returns
    -------
    dis : カメラから球までの距離[mm](キャリブレーションを用いた値を使用するためズレがある)
    """
    pxl = HEIGHT
    # y方向の焦点距離
    fy = 470
    # WebカメラのCMOSセンサー(1/4インチと仮定)の高さ[mm]
    camy = 2.7
    try:
        r = r * camy / pxl
        fy = fy * camy / pxl
        dis = RADIUS *  fy / r
    except ZeroDivisionError:
        dis = DETECTABLE_MAX_DIS
    return dis

if __name__ == "__main__":
    # 使用例
    cap = SetCamera(WIDTH, HEIGHT)
    start_time = time.time()
    # 決勝の競技時間+準備時間(12分)×トライ可能数(4回)×60秒
    while (time.time()-start_time<2880):
        # フレームをキャプチャ
        ret, frame = cap.read()
        # 色検出+輪郭検出
        x, y, dis, col = FindTarget(frame)

        # 小さすぎる円は球とみなさない(重要!)
        if dis < DETECTABLE_MAX_DIS:
            # コンソール表示
            print(x, y, dis, col)

        """ 
        デバッグ用　ESCキーで終了
        if cv2.waitKey(1) == 27:
            break
        """

    # 終了処理
    cap.release()

    # cv2.destroyAllWindows()   #デバッグ用　ウィンドウの終了

