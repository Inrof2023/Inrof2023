from const import const_setting as CST

def goback(ard_data :tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """
        フォトリフレクタの値からモータ―の動きを決める

        Parameters
        ----------
        ard_data : tuple[int, int, int, int]
            Arduinoから受け取った値
            left : int
                左のフォトリフレクタの値

            center_left : int
                真ん中の左のフォトリフレクタの値

            center_right : int
                真ん中の右のフォトリフレクタの値

            right : int
                右のフォトリフレクタの値

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
    left, center_left, center_right, right = ard_data
    next_state_num = 4

    # 逆左回転
    if ((left>CST.THRESHOLD and center_left>CST.THRESHOLD and center_right<=CST.THRESHOLD and right<=CST.THRESHOLD) or 
        (left>CST.THRESHOLD and center_left>CST.THRESHOLD and center_right<CST.THRESHOLD and right<=CST.THRESHOLD)):
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b101
    
    # 逆右回転
    elif ((left<=CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right>CST.THRESHOLD and right>CST.THRESHOLD) or 
          (left<=CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right>CST.THRESHOLD and right>CST.THRESHOLD)):
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b110

    # 後進
    elif (left>CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right<=CST.THRESHOLD and right>CST.THRESHOLD):
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b010

    # 全部黒なら停止してgoback -> goal
    elif (left<=CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right<=CST.THRESHOLD and right<=CST.THRESHOLD):
        next_state_num = 5
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b000

    # 停止
    else:
        dc_bit, serv_bit, step_bit = 0b1, 0b1, 0b000

    return next_state_num, dc_bit, serv_bit, step_bit