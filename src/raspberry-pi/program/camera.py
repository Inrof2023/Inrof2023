from typing import Tuple
import cv2
import numpy as np

# 赤い色の範囲を指定
LOWER_R1 = np.array([0, 64, 20])
UPPER_R1 = np.array([15, 255, 255])
LOWER_R2= np.array([225, 64, 20])
UPPER_R2 = np.array([255, 255, 255])

# 青色の範囲を指定
LOWER_B = np.array([130, 64, 20])
UPPER_B = np.array([175, 255, 255])

# 黄色の範囲を指定
LOWER_Y = np.array([20, 64, 20])
UPPER_Y = np.array([50, 255, 255])

# 球の半径[mm]
RADIUS = 32.5

# 取得画像の解像度
WIDTH = 320
HEIGHT = 240

# 球とみなす円形度
THRES_CIRCULARITY = 0.75

# 球を検出できる最大の距離
DETECTABLE_MAX_DIS = 1000

def set_camera(width: int, height: int):
    """
    Webカメラとcv2を使う準備

    Parameters
    ----------
    width : int
        取得画像の横の解像度
    
    height : int
        取得画像の縦の解像度

    Returns
    -------
    cap : 
        cv2のビデオキャプチャ
    """
    # カメラの設定
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


def find_target(frame) -> Tuple[int, int, int, int]:
    """
    一番近い球の座標，距離，色を取得する

    Parameters
    ----------
    frame : 
        取得画像

    Returns
    -------
    x[col] : int
        球の中心のx座標(ピクセル)

    y[col] : int
        球の中心のy座標(ピクセル)

    dis[col] : int
        球までの距離[mm](キャリブレーションを用いた値)

    col : int
        球の色(0:赤, 1:青, 2:黄)
    """
    x = np.zeros(3, dtype='float16')
    y = np.zeros(3, dtype='float16')
    dis = np.zeros(3, dtype='float16')
    r = np.zeros(3, dtype='float16')

    # 二値画像の取得
    (mask_red, mask_blue, mask_yellow) = masking(frame)
    
    for i, mask in enumerate([mask_red, mask_blue, mask_yellow]):
        # メディアンフィルタを適用する。
        mask = cv2.medianBlur(mask, ksize=5)

        # 色ごとに，最も近い球の座標と距離(とデバッグ用の半径)を取得
        x[i], y[i], dis[i], r[i] = get_coordinates_and_distance(mask)
        cv2.circle(frame,(int(x[i]),int(y[i])),int(r[i]),(0,255,0),2)   #デバッグ用　画面に円を表示する準備
    cv2.imshow("frame", frame)   #デバッグ用　画面に表示
    cv2.imshow("mask", mask_red + mask_blue + mask_yellow)   #デバッグ用　画面に表示

    # 最も近い球の色を取得する
    col = np.argmin(dis)
    return int(x[col]), int(y[col]), int(dis[col]), int(col)

def masking(frame):
    """
    赤，青，黄でマスキングして二値画像を取得する

    Parameters
    ----------
    frame : 
        取得画像

    Returns
    -------
    mask_red : 
        赤の二値画像

    mask_blue : 
        青の二値画像

    mask_yellow : 
        黄の二値画像

    """

    # 画像をHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
    # 赤,青,黄色の範囲内の領域を抽出(二値化)
    mask_red = cv2.inRange(hsv, LOWER_R1, UPPER_R1) + cv2.inRange(hsv, LOWER_R2, UPPER_R2)
    mask_blue = cv2.inRange(hsv, LOWER_B, UPPER_B)
    mask_yellow = cv2.inRange(hsv, LOWER_Y, UPPER_Y)
    
    return (mask_red, mask_blue, mask_yellow)

def get_coordinates_and_distance(mask) -> Tuple[float, float, float, float]:
    """
    二値画像から，距離が最も近い球の座標と距離を取得する

    Parameters
    ----------
    mask : 
        二値画像

    Returns
    x : np.ndarray
        最も近い球のx座標(ピクセル)
    
    y : np.ndarray
        最も近い球のy座標(ピクセル)

    dis : np.ndarray
        最も近い距離[mm](キャリブレーションを用いた値)

    r : np.ndarray
        最も近い球の半径(ピクセル)(デバッグ用)
    -------
    
    """
    # 輪郭検出
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        x = np.zeros(len(contours), dtype='float16')
        y = np.zeros(len(contours), dtype='float16')
        r = np.zeros(len(contours), dtype='float16')
        for i, cnt in enumerate(contours):
            # 輪郭の円形度を計算する
            cir = calc_circularity(cnt)
            if cir > THRES_CIRCULARITY:
                # 外接円の座標と半径を取得
                (x[i],y[i]),r[i] = cv2.minEnclosingCircle(cnt)
        # 最も半径の大きい球の配列番号を取得
        n = np.argmax(r)
        # 距離を計算
        dis = calc_distance(r[n])
        if dis == np.inf or dis >= DETECTABLE_MAX_DIS:
            dis = DETECTABLE_MAX_DIS
        return x[n], y[n], dis, r[n]
    else:
        return 0, 0, DETECTABLE_MAX_DIS, 0

def calc_circularity(cnt :np.ndarray) -> float:
    '''
    円形度を求める

    Parameters
    ----------
    cnt : np.ndarray
        輪郭の(x,y)座標の配列

    Returns
    -------
    cir : float
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

def calc_distance(r :float) -> float:
    """
    球の半径から距離を計算する

    Parameters
    ----------
    r : float
        フレーム中の球の半径(ピクセル)

    Returns
    -------
    dis : float
        カメラから球までの距離[mm](キャリブレーションを用いた値)
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

class Camera:
    def __init__(self):
        self.cap = set_camera(WIDTH, HEIGHT)

    def get_frame(self):
        # 使用例
        # フレームをキャプチャ
        ret, frame = self.cap.read()
        # 色検出+輪郭検出
        x, y, dis, col = find_target(frame)
        print("x:{}, y:{}, dis:{}, col:{}".format(x, y, dis, col))
        # ESCキーで終了
        if cv2.waitKey(1) == 27:
            # 終了処理
            self.cap.release()
            cv2.destroyAllWindows()   #デバッグ用　ウィンドウの終了
        return x, y, dis, col

"""
if __name__ == "__main__":
    # 使用例
    cap = set_camera(CST.WIDTH, CST.HEIGHT)
    start_time = time.time()
    while (time.time()-start_time<CST.GAMETIME):
        # フレームをキャプチャ
        ret, frame = cap.read()
        # 色検出+輪郭検出
        x, y, dis, col = find_target(frame)

        # 小さすぎる円は球とみなさない(重要!)
        if dis < CST.DETECTABLE_MAX_DIS:
            # デバッグ
            # print("x:{}, y:{}, dis:{}, col:{}".format(x, y, dis, col), end=" ")

        # ESCキーで終了
        if cv2.waitKey(1) == 27:
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()   #デバッグ用　ウィンドウの終了
    """
