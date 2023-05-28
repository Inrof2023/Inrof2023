from camera import Camera
from search import search
from detect import detect
from obtain import obtain
from redo import redo
from goback import goback
from goal import goal
from collections import deque

class Controller:
    def __init__(self):
        """
        self.now_state_num : int
        現在のロボットの状態を表す
            0 : search ライントレースを行う
            1 : detect カメラ情報を基にボールに近づく
            2 : obtain ボールを取る
            3 : redo   detectの時の動きを遡っていく
            4 : goback 後ろ向きでライントレースを行う
            5 : goal   ゴールに球を入れる

        his : Deque
            ステッピングモータの履歴を管理するキュー

        """
        self.next_state_num = 0
        self.his = deque()
        self.cam = Camera()

    def controller(self, ard_data: tuple[int, int, int, int]) -> tuple[int, int, int]:
        now_state_num = self.next_state_num
        cam_data = self.cam.get_frame()
        self.next_state_num, dc_bit, serv_bit, step_bit = self.determinate_state_and_movement(now_state_num, cam_data, ard_data)
        
        return dc_bit, serv_bit, step_bit

    def determinate_state_and_movement(self, now_state_num :int, cam_data :tuple[int, int, int, int], ard_data :tuple[int, int, int, int]) -> tuple[int, int, int]:
        """
        次の状態とモータ―の動きを決める

        Parameters
        ----------
        now_state : int
            現在のロボットの状態

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
        if now_state_num == 0:
            next_state_num, dc_bit, serv_bit, step_bit = search(cam_data, ard_data)

        elif now_state_num == 1:
            next_state_num, dc_bit, serv_bit, step_bit = detect(cam_data, self.his)

        elif now_state_num == 2:
            next_state_num, dc_bit, serv_bit, step_bit = obtain()

        elif now_state_num == 3:
            next_state_num, dc_bit, serv_bit, step_bit = redo(self.his)

        elif now_state_num == 4:
            next_state_num, dc_bit, serv_bit, step_bit = goback(ard_data)

        elif now_state_num == 5:
            next_state_num, dc_bit, serv_bit, step_bit = goal()

        return next_state_num, dc_bit, serv_bit, step_bit

