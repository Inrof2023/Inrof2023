from const import const_setting as CST

def search(cam_data :tuple[int, int, int, int], ard_data :tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """
        フォトリフレクタの値からモータ―の動きを決める
        カメラとボールの距離から次の状態を決める

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
    _, _, dis, _ = cam_data

    # 左回転
    if ((left>CST.THRESHOLD and center_left>CST.THRESHOLD and center_right<=CST.THRESHOLD and right<=CST.THRESHOLD) or 
        (left>CST.THRESHOLD and center_left>CST.THRESHOLD and center_right>CST.THRESHOLD and right<=CST.THRESHOLD)):
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b011
    
    # 右回転
    elif ((left<=CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right>CST.THRESHOLD and right>CST.THRESHOLD) or 
          (left<=CST.THRESHOLD and center_left>CST.THRESHOLD and center_right>CST.THRESHOLD and right>CST.THRESHOLD)):
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b100

    # 前進
    elif (left>CST.THRESHOLD and center_left<=CST.THRESHOLD and center_right<=CST.THRESHOLD and right>CST.THRESHOLD):
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b001

    # 後進（真っ白の時）
    elif (left>CST.THRESHOLD and center_left>CST.THRESHOLD and center_right>CST.THRESHOLD and right>CST.THRESHOLD):
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b010

    # 停止
    else:
        dc_bit, serv_bit, step_bit = 0b0, 0b0, 0b000

    # ボールを発見したらsearch -> detect
    if (dis < CST.DETECTABLE_MAX_DIS):
        next_state_num = 1
    else:
        next_state_num = 0

    return next_state_num, dc_bit, serv_bit, step_bit
