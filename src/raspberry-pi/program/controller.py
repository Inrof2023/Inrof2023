from camera import Camera
from robot_status import RobotStatus
from utils import *

class Controller:
    def __init__(self):
        """
        next_state : State
        現在のロボットの状態を表す
            LINETRACE : ライントレースをさせる
            FREEBALL : フリーボールをゴールに入れる
            SEARCH : ボールを探す
            DETECT : カメラ情報を基にボールに近づく
            OBTAIN : ボールを取る
            GOBACK : detectの時の動きを遡っていく
            LOOKBACK : 180度方向転換する
            GOAL : ゴールに球を入れる
        """
        self.next_state = State.READY
        self.cam = Camera()
        self.rbst = RobotStatus()

    def controller(self, left: int, center_left: int, center_right: int, right: int) -> tuple[int, int, int, int, int]:
        now_state = self.next_state
        
        if now_state ==State.READY:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.ready(left, center_left, center_right, right)

        elif now_state ==State.FREEBALL:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.freeball(left, center_left, center_right, right)

        elif now_state ==State.LINETRACE:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.linetrace(left, center_left, center_right, right)

        elif now_state == State.SEARCH:
            x, y, dis, col = self.cam.get_frame()
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.search(dis)

        elif now_state == State.DETECT:
            x, y, dis, col = self.cam.get_frame()
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.detect(x, y, dis, col)

        elif now_state == State.OBTAIN:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.obtain()

        elif now_state == State.GOBACK:
            x, y, dis, col = self.cam.get_frame()
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.goback()

        elif now_state == State.LOOKBACK:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.lookback()

        elif now_state == State.GOAL:
            self.next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit = self.rbst.goal()

        return dir_bit, trace_bit, dc_bit, serv_bit, step_bit
