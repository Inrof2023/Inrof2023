from collections import deque
from utils import *
import time

# 吸引可能な領域のx座標の最小値
X_MIN = 130

# 吸引可能な領域のx座標の最大値
X_MAX = 190

# 吸引可能な領域のy座標の最小値
Y_MIN = 100

# 吸引可能な領域のy座標の最大値
Y_MAX = 240

# 球を吸引できる最大の距離
OBTAINABLE_MAX_DIS = 200

# 球を検出できる最大の距離
DETECTABLE_MAX_DIS = 1000

# ボールがあるエリアにいるかを，全部黒いラインを超えた回数で認識する
ALL_BLACK_LINE_COUNT_READY_TO_SEARCH = 0

# 赤にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_RED_GOAL = 0

# 青にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_BLUE_GOAL = 0

# 黄にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_YELLOW_GOAL = 0

class RobotStatus:
    def __init__(self):
        """
        his : Deque
            ステッピングモータの履歴を管理するキュー
        """
        self.his = deque()
        self.all_black_line_count = 0
        self.last_all_blak_line_flag = False
        self.now_obtain_color = 0
        self.start_t = 0
        self.instructure_runtime = {State.LINETRACE:[],
                                    State.SEARCH:[],
                                    State.DETECT:[],
                                    State.OBTAIN:[1, 5, 10],
                                    State.GOBACK:[],
                                    State.GOAL: [1, 5]}
                                              
    def detect_all_black_line(self, left: int, center_left: int, center_right: int, right: int) -> None:
        line_sensor = LineSensor(left, center_left, center_right, right)
        # 全部黒の線に乗ったらフラグを立てる
        if ((not self.last_all_blak_line_flag) and (line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.last_all_blak_line_flag = True
        # 全部黒の線を超えたらカウントする
        elif ((self.last_all_blak_line_flag) and (line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.all_black_line_count += 1
            self.last_all_blak_line_flag = False

    def linetrace(self) -> tuple[State, int, int, int, int, int]:
        """
            ライントレースをしている
            Parameters
            ----------

            Returns
            -------
        """
        next_state = State.SEARCH
        dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
        trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def search(self, dis: int) -> tuple[State, int, int, int, int, int]:
        """
            ボールを探している
            ステッピングモータの履歴を保存する
            Parameters
            ----------

            Returns
            -------
        """
        # 検出可能距離以内にボールを発見したらsearch -> detect
        if dis<DETECTABLE_MAX_DIS:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            self.his.append(SteppingMotorMotion.STOP)
            next_state = State.DETECT
        else:
            # 前進
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            self.his.append(SteppingMotorMotion.FORWARD)
            next_state = State.SEARCH
                
        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def detect(self, x: int, y: int, dis: int, col: int) -> tuple[State, int, int, int, int, int]:
        """
        カメラの値からモータ―の動きを決める
        ステッピングモータの履歴を保存する

        Parameters
        ----------

        Returns
        -------
        """
        # 範囲内にボールが来ていれば停止してdetect -> obtain
        if (x>X_MIN and x<X_MAX and y>Y_MIN and y<Y_MAX and dis<OBTAINABLE_MAX_DIS):
            self.now_obtain_color = col
            next_state = State.OBTAIN
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.his.append(SteppingMotorMotion.STOP)
        # 検出範囲外ならSEARCHに戻る
        elif (dis>=DETECTABLE_MAX_DIS):
            next_state = State.SEARCH
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.his.append(SteppingMotorMotion.STOP)
        # 右回転
        elif (x<X_MIN):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
            self.his.append(SteppingMotorMotion.RIGHTWARD)
        # 左回転
        elif (x>X_MAX):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.his.append(SteppingMotorMotion.LEFTWARD)
        # 前進
        else:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.his.append(SteppingMotorMotion.FORWARD)
    
        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def obtain(self) -> tuple[State, int, int, int, int, int]:
        """
        DCモータとサーボモータを動かす

        Parameters
        ----------

        Returns
        -------
        """
        if time.time()-self.start_t < self.instructure_runtime[State.OBTAIN][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.start_t = time.time()
            next_state = State.OBTAIN

        # DCモータを回す
        elif time.time()-self.start_t < self.instructure_runtime[State.OBTAIN][1]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.OBTAIN
        # サーボモータを上げる
        elif time.time()-self.start_t < self.instructure_runtime[State.OBTAIN][2]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.OBTAIN
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.start_t = 0
            next_state = State.GOBACK
        
        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def goback(self) -> tuple[State, int, int, int, int, int]:
        """
        detect状態の時のモータの値を遡る

        Parameters
        ----------

        Returns
        -------
        """

        # 履歴を辿る
        if len(self.his) != 0:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
            next_state = State.GOBACK
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.GOAL

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def goal(self) -> tuple[State, int, int, int, int, int]:
        """
        ゴールする

        Parameters
        ----------

        Returns
        -------
        """
        if time.time()-self.start_t < self.instructure_runtime[State.GOAL][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.start_t = time.time()
            next_state = State.GOAL
        # DCモータを止めてサーボモータを下げる
        elif time.time()-self.start_t < self.instructure_runtime[State.GOAL][1]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.GOAL
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.SEARCH
            self.start_t = 0

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit
