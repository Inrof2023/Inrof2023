from collections import deque
from pickle import STOP
from utils import *
import time

# 吸引可能な領域のx座標の最小値
X_MIN = 100

# 吸引可能な領域のx座標の最大値
X_MAX = 220

# 吸引可能な領域のy座標の最小値
Y_MIN = 120

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


# DETECT中にボールを見失ったとみなすボール追跡実行回数
DETECT_HIS_LENGTH_LIMIT = 150

# DCモータを動かす実行回数
DC_STEP = 150

# サーボモータを動かす実行回数
SV_STEP = 100

# ステッピングモータで前進/後進する実行回数
FB_STEP = 100

# ステッピングモータで左/右前進する実行回数
LR_STEP = 100

# 待機の実行回数
WAIT_STEP = 200

# 実行回数をカウントし始める準備
ONE_STEP = 1

# 黒い線かチェックするために左/右 前進する実行回数
LR_STEP_TO_CHECK_ALL_BLACK_LINE = 5
class RobotStatus:
    def __init__(self):
        """
        his : Deque
            ステッピングモータの履歴を管理するキュー
        """
        self.his = deque()
        self.all_black_line_count = 0
        self.last_all_black_line_flag = False
        self.check_all_black_line_flag = False
        self.left_or_right = SteppingMotorMotion.STOP
        self.now_obtain_color = 0
        self.execute_count = 0
        self.search_road_num = 0
        self.search_his_length = 0
        self.detect_missing_flag = False
        self.instruction_steps = {State.LINETRACE:[LR_STEP_TO_CHECK_ALL_BLACK_LINE],
                                  State.SEARCH:[self.search_road_num*FB_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP+LR_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP+LR_STEP+FB_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP,
                                                self.search_road_num*FB_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP+LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_STEP],
                                  State.DETECT:[],
                                  State.OBTAIN:[ONE_STEP, 
                                                ONE_STEP+DC_STEP, 
                                                ONE_STEP+DC_STEP+SV_STEP],
                                  State.GOBACK:[],
                                  State.LOOKBACK:[ONE_STEP,
                                                  ONE_STEP+LR_STEP,
                                                  ONE_STEP+LR_STEP+FB_STEP,
                                                  ONE_STEP+LR_STEP+FB_STEP+LR_STEP,
                                                  ONE_STEP+LR_STEP+FB_STEP+LR_STEP+FB_STEP],
                                  State.GOAL: [ONE_STEP, 
                                               ONE_STEP+DC_STEP,
                                               ONE_STEP+DC_STEP+WAIT_STEP]}

    def ready(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int, int, int]:
        if left+center_left+center_right+right<2000:
            next_state = State.READY
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        else:
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit
    def linetrace(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int, int, int]:
        """
            ライントレースをしている
            Parameters
            ----------

            Returns
            -------
        """
        line_sensor = LineSensor(left, center_left, center_right, right)
        # 全部黒の線を超えたらカウントしてLINETRACE -> SEARCH
        if (self.last_all_black_line_flag and line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK)):
            print("こえた")
            self.all_black_line_count += 1
            self.last_all_black_line_flag = False
            self.execute_count = 0
            self.check_all_black_line_flag = False
            self.left_or_right = SteppingMotorMotion.STOP
            next_state = State.SEARCH
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 全部黒の線に乗ったら乗ったフラグを立てる
        elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
            print("のった")
            self.last_all_black_line_flag = True
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 左以外黒い線になった瞬間，ライントレースを一旦切って黒い線かチェックするフラグを立てる
        elif (not self.check_all_black_line_flag and line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.BLACK)):
            print("のった?")
            self.check_all_black_line_flag = True
            self.left_or_right = SteppingMotorMotion.LEFTWARD
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
        # 右以外黒い線になった瞬間，ライントレースを一旦切って黒い線かチェックするフラグを立てる
        elif ((not self.check_all_black_line_flag) and line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.WHITE)):
            print("のった?")
            self.check_all_black_line_flag = True
            self.left_or_right = SteppingMotorMotion.RIGHTWARD
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
        # 黒い線かチェックするために左または右に少し進む
        elif (self.check_all_black_line_flag and self.execute_count<self.instruction_steps[State.LINETRACE][0]):
            self.execute_count += 1
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.left_or_right)
        # 左または右に少し進み切ったら，チェックフラグをFalseにしてtrace_bitをONにする
        elif (self.check_all_black_line_flag and self.execute_count>=self.instruction_steps[State.LINETRACE][0]):
            self.execute_count = 0
            self.check_all_black_line_flag = False
            self.left_or_right = SteppingMotorMotion.STOP
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # ライントレース
        else:
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
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
            self.search_his_length = len(self.his)
            self.execute_count = 0
            next_state = State.DETECT
        else:
            # 前進(探索路search_road_numに依存)
            if self.execute_count < self.instruction_steps[State.SEARCH][0]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.FORWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 左前進 (search内で履歴を遡る際の終了位置その1)
            elif self.execute_count < self.instruction_steps[State.SEARCH][1]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.LEFTWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 前進
            elif self.execute_count < self.instruction_steps[State.SEARCH][2]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.FORWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 履歴を(search内で履歴を遡る際の終了位置その1)まで遡る
            elif self.execute_count < self.instruction_steps[State.SEARCH][3]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.execute_count += 1
                next_state = State.SEARCH
            # 右前進 (search内で履歴を遡る際の終了位置その2)
            elif self.execute_count < self.instruction_steps[State.SEARCH][4]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.RIGHTWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 前進
            elif self.execute_count < self.instruction_steps[State.SEARCH][5]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.FORWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 履歴を(search内で履歴を遡る際の終了位置その2)まで遡る
            elif self.execute_count < self.instruction_steps[State.SEARCH][6]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.execute_count += 1
                next_state = State.SEARCH
            # 前進
            elif self.execute_count < self.instruction_steps[State.SEARCH][7]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.FORWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 実行回数をself.search_road_num * FB_STEPまで戻し，探索済みの道番号を更新
            else:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.STOP)
                self.execute_count = self.search_road_num * FB_STEP
                self.search_road_num += 1
                next_state = State.SEARCH
        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def detect(self, x: int, y: int, dis: int, col: int) -> tuple[State, int, int, int, int, int]:
        """
        カメラの値からモータ―の動きを決める
        ステッピングモータの履歴を保存する
        DCモータは回し続ける

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
            self.execute_count = 0
            self.search_his_length = 0
            self.detect_missing_flag = False
        # 前進
        elif dis >= OBTAINABLE_MAX_DIS:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.his.append(SteppingMotorMotion.FORWARD)
            self.execute_count = 0
            self.detect_missing_flag = False
        # 右回転
        elif (x<X_MIN):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
            self.his.append(SteppingMotorMotion.RIGHTWARD)
            self.execute_count = 0
            self.detect_missing_flag = False
        # 左回転
        elif (x>=X_MAX):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.his.append(SteppingMotorMotion.LEFTWARD)
            self.execute_count = 0
            self.detect_missing_flag = False
        #　見失ったフラグがTrueで遡りきってない時DETECT中の履歴を遡る
        elif self.detect_missing_flag and self.execute_count < DETECT_HIS_LENGTH_LIMIT:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
            self.execute_count += 1
        #　見失ったフラグがTrueで遡りきったらDCモータを切りSEARCHに戻る
        elif self.detect_missing_flag and self.execute_count >= DETECT_HIS_LENGTH_LIMIT:
            next_state = State.SEARCH
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.his.append(SteppingMotorMotion.STOP)
            self.execute_count = self.search_road_num * FB_STEP
            self.detect_missing_flag = False
        # ステッピングモータの履歴が長すぎたら見失ったフラグを立てる
        elif len(self.his)-self.search_his_length >= DETECT_HIS_LENGTH_LIMIT:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.his.append(SteppingMotorMotion.STOP)
            self.detect_missing_flag = True
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
        if self.execute_count < self.instruction_steps[State.OBTAIN][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.OBTAIN

        # DCモータを回す
        elif self.execute_count < self.instruction_steps[State.OBTAIN][1]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.OBTAIN
        # サーボモータを上げる
        elif self.execute_count < self.instruction_steps[State.OBTAIN][2]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.OBTAIN
        # DCモータを切る
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count = 0
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
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
            next_state = State.GOBACK
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            next_state = State.LOOKBACK

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def lookback(self) -> tuple[State, int, int, int, int, int]:
        """
        180度方向転換する

        Parameters
        ----------

        Returns
        -------
        """
        dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
        trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        next_state = State.GOAL

        """
        if self.execute_count < self.instruction_steps[State.LOOKBACK][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.LOOKBACK
        # 左後進
        elif self.execute_count < self.instruction_steps[State.LOOKBACK][1]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
            self.execute_count += 1
            next_state = State.LOOKBACK
        # 前進
        elif self.execute_count < self.instruction_steps[State.LOOKBACK][2]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.execute_count += 1
            next_state = State.LOOKBACK
        # 左後進
        elif self.execute_count < self.instruction_steps[State.LOOKBACK][3]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
            self.execute_count += 1
            next_state = State.LOOKBACK
        # 前進
        elif self.execute_count < self.instruction_steps[State.LOOKBACK][4]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.execute_count += 1
            next_state = State.LOOKBACK
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count = 0
            next_state = State.GOAL
        """

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit


    def goal(self) -> tuple[State, int, int, int, int, int]:
        """
        ゴールする

        Parameters
        ----------

        Returns
        -------
        """
        if self.execute_count < self.instruction_steps[State.GOAL][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.GOAL
        # サーボモータを下げる
        elif self.execute_count < self.instruction_steps[State.GOAL][1]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.GOAL
        # 待機
        elif self.execute_count < self.instruction_steps[State.GOAL][2]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            self.now_obtain_color = 0
            next_state = State.GOAL
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count = 0
            next_state = State.SEARCH

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit
