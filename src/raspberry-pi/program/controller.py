from camera import Camera
from robot_status import RobotStatus
from utils import *

class Controller:
    def __init__(self):
        """
        next_state : State
        現在のロボットの状態を表す
            LINETRACE : ライントレースをさせる
            SEARCH : ボールを探す
            DETECT : カメラ情報を基にボールに近づく
            OBTAIN : ボールを取る
            GOBACK : detectの時の動きを遡っていく
            GOAL : ゴールに球を入れる
        """
        self.next_state = State.LINETRACE
        self.cam = Camera()
        self.rbst = RobotStatus()

    def controller(self, left: int, center_left: int, center_right: int, right: int) -> tuple[int, int, int, int, int]:
        now_state = self.next_state
        if now_state ==State.LINETRACE:
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.linetrace()

        elif now_state == State.SEARCH:
            x, y, dis, col = self.cam.get_frame()
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.search(dis)

        elif now_state == State.DETECT:
            x, y, dis, col = self.cam.get_frame()
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.detect(x, y, dis, col)

        elif now_state == State.OBTAIN:
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.obtain()

        elif now_state == State.GOBACK:
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.goback()
        if now_state == State.GOAL:
            dir_bit = 0b0
            trace_bit = 0b0
            self.next_state, dc_bit, serv_bit, step_bit = self.rbst.goal()

        return dir_bit, trace_bit, dc_bit, serv_bit, step_bit

        """
        次の状態とモータ―の動きを決める

        Parameters
        ----------
        now_state : State
            現在のロボットの状態

        カメラから受け取った値
            x : int
                球の中心のx座標(ピクセル)

            y : int
                球の中心のy座標(ピクセル)

            dis : int
                球までの距離[mm](キャリブレーションを用いた値)

            col : int
                球の色(0:赤, 1:青, 2:黄)

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
        next_state : State
            次のロボットの状態

        DIR_BIT: int
            1bit
            ライントレースをする時の向き
            0: 前進, 1: 後進

        TRACE_BIT: int
            1bit
            ライントレースをするかどうか
            0: ライントレースしない(Raspberry Piが制御), 1: ライントレースする(Arduinoが制御)

        DC_BIT: int
            1bit
            DCモータの制御ビット
            0: 停止, 1: 動作
    
        SERV_BIT: int
            1bit
            サーボモータの制御ビット
            0: 停止, 1: 動作
    
        STEP_BIT: int
            4bit
            ステッピングモータの制御ビット
            0000: 停止, 0001: 前進, 0010: 後退, 0011: 左回転, 0100: 右回転　0101: 左後回転, 0110: 右後回転, 0111: 左旋回, 1000: 右旋回
        """