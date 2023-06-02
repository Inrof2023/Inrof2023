from camera import Camera
from states import search, detect, obtain, redo, goback, goal, LineType, LineSensor
from collections import deque

# ボールがあるエリアにいるかを，全部黒いラインを超えた回数で認識する
ALL_BLACK_LINE_COUNT_FOR_GET_TO_READY = 4

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
        self.all_black_line_count = 0
        self.now_obtain_color = 0
        self.last_all_blak_line_flag = False
        self.isDetectable = False

    def controller(self, left: int, center_left: int, center_right: int, right: int) -> tuple[int, int, int, int, int]:
        now_state_num = self.next_state_num
        x, y, dis, col = self.cam.get_frame()
        self.next_state_num, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.determinate_state_and_movement(now_state_num, x, y, dis, col, left, center_left, center_right, right)
        
        return dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def detect_all_black_line(self, left: int, center_left: int, center_right: int, right: int) -> None:
        line_sensor = LineSensor(left, center_left, center_right, right)
        if ((not self.last_all_blak_line_flag) and (line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.last_all_blak_line_flag = True
        elif ((self.last_all_blak_line_flag) and (line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.all_black_line_count += 1
            self.last_all_blak_line_flag = False
        if self.all_black_line_count>ALL_BLACK_LINE_COUNT_FOR_GET_TO_READY:
            self.all_black_line_count = 0
            self.isDetectable = True

    def determinate_state_and_movement(self, now_state_num :int, x: int, y: int, dis: int, col: int, left: int, center_left: int, center_right: int, right: int) -> tuple[int, int, int, int, int, int]:
        """
        次の状態とモータ―の動きを決める

        Parameters
        ----------
        now_state : int
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
        next_state_num : int
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

        if now_state_num == 0:
            self.detect_all_black_line(left, center_left, center_right, right)
            dir_bit = 0b0
            trace_bit = 0b1
            next_state_num, dc_bit, serv_bit, step_bit = search(dis, self.isDetectable)

        elif now_state_num == 1:
            dir_bit = 0b0
            trace_bit = 0b0
            next_state_num, dc_bit, serv_bit, step_bit = detect(x, y, dis, self.his)

        elif now_state_num == 2:
            self.now_obtain_color = col
            dir_bit = 0b0
            trace_bit = 0b0
            next_state_num, dc_bit, serv_bit, step_bit = obtain()

        elif now_state_num == 3:
            dir_bit = 0b1
            trace_bit = 0b0
            next_state_num, dc_bit, serv_bit, step_bit = redo(self.his)

        elif now_state_num == 4:
            self.detect_all_black_line(left, center_left, center_right, right)
            dir_bit = 0b1
            trace_bit = 0b1
            next_state_num, dc_bit, serv_bit, step_bit = goback(self.now_obtain_color, self.all_black_line_count, left, center_left, center_right, right)

        elif now_state_num == 5:
            dir_bit = 0b0
            trace_bit = 0b0
            next_state_num, dc_bit, serv_bit, step_bit = goal()

        return next_state_num, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

