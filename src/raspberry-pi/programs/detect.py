from const import const_setting as CST
from typing import Deque

def detect(cam_data  :tuple[int, int, int, int], his :Deque) -> tuple[int, int, int, int]:
    """
    カメラの値からモータ―の動きを決める
    ステッピングモータの履歴を保存する

    Parameters
    ----------
    cam_data : tuple[int, int, int, int]
        カメラから受け取った値
        x[col] : int
            球の中心のx座標(ピクセル)

        y[col] : int
            球の中心のy座標(ピクセル)

        dis[col] : int
            球までの距離[mm](キャリブレーションを用いた値)

        col : int
            球の色(0:赤, 1:青, 2:黄)

    his : Deque
        ステッピングモータの履歴を管理するキュー

    Returns
    -------
    next_state_num : int
            次のロボットの状態

    dc_bit: int
        1bit
        DCモータの制御ビット
        0: 停止, 1: 動作
    
    serv_bit: int
        1bit
        サーボモータの制御ビット
        0: 停止, 1: 動作
    
    step_bit: int
        3bit
        ステッピングモータの制御ビット
    000: 停止, 001: 前進, 010: 後退, 011: 左回転, 100: 右回転　101: 左後回転, 110: 右後回転
    """
    x, y, dis, col = cam_data

    # ボールの検出可能範囲から外れたら全モータを停止してsearchに戻る
    # また，ステッピングモータの履歴をリセットする
    if (dis>=CST.DETECTABLE_MAX_DIS):
        next_state_num = 0
        his.clear()
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b000

    # カメラを左に90度傾けているため座標に注意
    # 左回転
    elif (y<CST.Y_MIN):
        next_state_num = 1
        dc_bit, serv_bit, step_bit = 0b1, 0b0, 0b011
    
    # 右回転
    elif (y>CST.Y_MAX):
        next_state_num = 1
        dc_bit, serv_bit, step_bit = 0b1, 0b0, 0b100

    # 範囲内にボールが来ていれば停止してdetect -> obtain
    elif (x>CST.X_MIN and x<CST.X_MAX and y>CST.Y_MIN and y<CST.Y_MAX and dis<CST.OBTAINABLE_MAX_DIS):
        next_state_num = 2
        dc_bit, serv_bit, step_bit = 0b1, 0b0, 0b000

    # 前進
    else:
        next_state_num = 1
        dc_bit, serv_bit, step_bit = 0b1, 0b0, 0b001

    his.append(step_bit)

    return next_state_num, dc_bit, serv_bit, step_bit
    
