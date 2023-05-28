import const_setting
import numpy as np

# フォトリフレクタの閾値
const_setting.THRESHOLD = 400

# 吸引可能な領域のx座標の最v小値
const_setting.X_MIN = 10

# 吸引可能な領域のx座標の最大値
const_setting.X_MAX = 90

# 吸引可能な領域のy座標の最小値
const_setting.Y_MIN = 100

# 吸引可能な領域のy座標の最大値
const_setting.Y_MAX = 140

# 球を吸引できる最大の距離
const_setting.OBTAINABLE_MAX_DIS = 180

# 球を検出できる最大の距離
const_setting.DETECTABLE_MAX_DIS = 1000

# サーボを動かす時間
const_setting.SERV_TIMEOUT = 3

# 赤い色の範囲を指定
const_setting.LOWER_R1 = np.array([0, 64, 20])
const_setting.UPPER_R1 = np.array([15, 255, 255])
const_setting.LOWER_R2= np.array([225, 64, 20])
const_setting.UPPER_R2 = np.array([255, 255, 255])

# 青色の範囲を指定
const_setting.LOWER_B = np.array([130, 64, 20])
const_setting.UPPER_B = np.array([175, 255, 255])

# 黄色の範囲を指定
const_setting.LOWER_Y = np.array([20, 64, 20])
const_setting.UPPER_Y = np.array([50, 255, 255])

# 球の半径[mm]
const_setting.RADIUS = 32.5

# 取得画像の解像度
const_setting.WIDTH = 320
const_setting.HEIGHT = 240

# 球とみなす円形度
const_setting.THRES_CIRCULARITY = 0.75

# 決勝の競技時間+準備時間(12分)×トライ可能数(4回)×60秒
const_setting.GAMETIME = 2880
