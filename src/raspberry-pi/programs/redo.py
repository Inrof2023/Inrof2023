from typing import Deque

def redo(his :Deque) -> tuple[int, int, int, int]:
    """
    detect状態の時のモータの値を遡る

    Parameters
    ----------
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
        000: 停止, 001: 前進, 010: 後退, 011: 左回転, 100: 右回転, 101: 左後回転, 110: 右後回転
    """
    if len(his) == 0:
        next_state_num = 4
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b000
    else:
        next_state_num = 3
        pre_step_bit = his.pop()
        dc_bit, serv_bit, step_bit = 0b1, 0b1, pre_step_bit
    return next_state_num, dc_bit, serv_bit, step_bit
    
