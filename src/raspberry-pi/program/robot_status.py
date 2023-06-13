from collections import deque
from enum import Enum
from utils import *
import time

# 吸引可能な領域のx座標の最小値
X_MIN = 110

# 吸引可能な領域のx座標の最大値
X_MAX = 210

# 吸引可能な領域のy座標の最小値
Y_MIN = 120

# 吸引可能な領域のy座標の最大値
Y_MAX = 240

# 球を吸引できる最大の距離
OBTAINABLE_MAX_DIS = 200

# 球を検出できる最大の距離
DETECTABLE_MAX_DIS = 1000

class AllBlackLineThres(Enum):
    TO_FREEBALL = 0,
    TO_SEARCH = 1,
    TO_BLUE = 2,
    TO_YELLOW = 3,
    TO_RED = 4,
    AFTER_BLUE = 5,
    AFTER_YELLOW = 6,
    AFTER_RED = 7,

ALLBLACKLINE_COUNT_AND_NEXT = {AllBlackLineThres.TO_FREEBALL:[1, State.FREEBALL],
                               AllBlackLineThres.TO_SEARCH:[2, State.SEARCH], 
                               AllBlackLineThres.TO_BLUE:[1, State.GOAL],
                               AllBlackLineThres.TO_YELLOW:[1, State.GOAL],
                               AllBlackLineThres.TO_RED:[1, State.GOAL],
                               AllBlackLineThres.AFTER_BLUE:[1, State.SEARCH],
                               AllBlackLineThres.AFTER_YELLOW:[1, State.SEARCH],
                               AllBlackLineThres.AFTER_RED:[1, State.SEARCH]}

# DETECT中にボールを見失ったとみなすボール追跡実行回数
DETECT_HIS_LENGTH_LIMIT = 150

# DCモータを動かす実行回数
DC_STEP = 150

# サーボモータを動かす実行回数
SV_STEP = 100

# DCモータを動かす実行回数
DC_STEP = 150

# ステッピングモータで前進/後進する実行回数
FB_STEP = 100

# ステッピングモータで左/右前進する実行回数
LR_STEP = 100

# ステッピングモータでBLUE GOAL前に前進する実行回数
FB_STEP_BEFORE_BLUE_GOAL = 250

# ステッピングモータでBLUE GOAL後に前進する実行回数
FB_STEP_AFTER_BLUE_GOAL = 200

# linetrace little前進/後進する実行回数
FB_LITTLE_STEP = 40

# linetrace little前進/後進する実行回数(while camera using)
FB_LITTLE_STEP_CAM_USING = 20

# 待機の実行回数
WAIT_STEP = 20

# 実行回数をカウントし始める準備
ONE_STEP = 1

# 黒い線かチェックするために左/右 前進する実行回数
LR_STEP_TO_CHECK_ALL_BLACK_LINE = 10

class RobotStatus:
    def __init__(self):
        """
        his : Deque
            ステッピングモータの履歴を管理するキュー
        """
        self.his = deque()
        self.all_black_line_count = 0
        self.linetrace_next = AllBlackLineThres.TO_FREEBALL
        self.last_all_black_line_flag = False
        self.check_all_black_line_flag = False
        self.left_or_right = SteppingMotorMotion.STOP
        self.up_or_down = ServoMotorMotion.DOWN
        self.now_obtain_color = 0
        self.execute_count = 0
        self.freeball_goal_position_flag = False
        self.search_road_num = 0
        self.detect_missing_flag = False
        self.instruction_steps = {State.READY:[],
                                  State.FREEBALL:[ONE_STEP,
                                                  ONE_STEP+SV_STEP,
                                                  ONE_STEP+SV_STEP+ONE_STEP,
                                                  ONE_STEP+SV_STEP+ONE_STEP+FB_LITTLE_STEP],
                                  State.LINETRACE:[LR_STEP_TO_CHECK_ALL_BLACK_LINE],
                                  State.SEARCH:[LR_STEP,
                                                LR_STEP+FB_STEP,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING+LR_STEP,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING+LR_STEP+FB_STEP,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING+LR_STEP+FB_STEP+FB_STEP+LR_STEP,
                                                LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING+LR_STEP+FB_STEP+FB_STEP+LR_STEP+FB_LITTLE_STEP_CAM_USING],
                                  State.DETECT:[],
                                  State.OBTAIN:[ONE_STEP, 
                                                ONE_STEP+DC_STEP, 
                                                ONE_STEP+DC_STEP+SV_STEP],
                                  State.GOBACK:[],
                                  State.LOOKBACK:[FB_LITTLE_STEP],
                                  State.GOAL: [[[]], #now_obtain_color=0 non instruction
                                               [[ONE_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+FB_STEP_BEFORE_BLUE_GOAL,SteppingMotorMotion.FORWARD],
                                                [ONE_STEP+FB_STEP_BEFORE_BLUE_GOAL+DC_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+FB_STEP_BEFORE_BLUE_GOAL+DC_STEP+ONE_STEP,SteppingMotorMotion.LOOKBACK],
                                                [ONE_STEP+FB_STEP_BEFORE_BLUE_GOAL+DC_STEP+ONE_STEP+FB_STEP_AFTER_BLUE_GOAL,SteppingMotorMotion.FORWARD]],
                                               [[ONE_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+ONE_STEP,SteppingMotorMotion.LEFTWARD90],
                                                [ONE_STEP+ONE_STEP+DC_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+ONE_STEP+DC_STEP+ONE_STEP,SteppingMotorMotion.RIGHTBACK90],
                                                [ONE_STEP+ONE_STEP+DC_STEP+ONE_STEP+WAIT_STEP,SteppingMotorMotion.STOP]],
                                               [[ONE_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+ONE_STEP,SteppingMotorMotion.LEFTWARD90],
                                                [ONE_STEP+ONE_STEP+DC_STEP,SteppingMotorMotion.STOP],
                                                [ONE_STEP+ONE_STEP+DC_STEP+ONE_STEP,SteppingMotorMotion.RIGHTBACK90],
                                                [ONE_STEP+ONE_STEP+DC_STEP+ONE_STEP+FB_STEP,SteppingMotorMotion.FORWARD]]]}

    def ready(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int, int, int]:
        if left+center_left+center_right+right<2000:
            next_state = State.READY
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        else:
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit

    def freeball(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int, int, int]:
        """
            フリーボールををゴールに入れる
            Parameters
            ----------

            Returns
            -------
        """
        line_sensor = LineSensor(left, center_left, center_right, right)
        # 値を超えたらflag true
        if self.all_black_line_count >= ALLBLACKLINE_COUNT_AND_NEXT[self.linetrace_next][0]:
            self.all_black_line_count = 0
            self.freeball_goal_position_flag = True
            self.linetrace_next = AllBlackLineThres.TO_SEARCH
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # right ward 90
        elif self.freeball_goal_position_flag and self.execute_count<self.instruction_steps[State.FREEBALL][0]:
            self.execute_count += 1
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD90)
        # servo down
        elif self.freeball_goal_position_flag and self.execute_count<self.instruction_steps[State.FREEBALL][1]:
            self.execute_count += 1
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # right back 90
        elif self.freeball_goal_position_flag and self.execute_count<self.instruction_steps[State.FREEBALL][2]:
            self.execute_count += 1
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTBACK90)
        # forward
        elif self.freeball_goal_position_flag and self.execute_count<self.instruction_steps[State.FREEBALL][3]:
            self.execute_count += 1
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
        # freeball -> linetrace
        elif self.freeball_goal_position_flag and self.execute_count>=self.instruction_steps[State.FREEBALL][3]:
            self.execute_count = 0
            self.all_black_line_count = 1
            self.freeball_goal_position_flag = False
            self.linetrace_next = AllBlackLineThres.TO_SEARCH
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        
        # 全部黒の線を超えたらカウントする
        elif (self.last_all_black_line_flag and line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK)):
            print("こえた")
            self.all_black_line_count += 1
            self.last_all_black_line_flag = False
            self.execute_count = 0
            self.check_all_black_line_flag = False
            self.left_or_right = SteppingMotorMotion.STOP
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 全部黒の線に乗ったら乗ったフラグを立てる
        elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
            print("のった")
            self.last_all_black_line_flag = True
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
        # 左以外黒い線になった瞬間，ライントレースを一旦切って黒い線かチェックするフラグを立てる
        elif (not self.check_all_black_line_flag and line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.BLACK)):
            print("のった?")
            self.check_all_black_line_flag = True
            self.left_or_right = SteppingMotorMotion.LEFTWARD
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
        # 右以外黒い線になった瞬間，ライントレースを一旦切って黒い線かチェックするフラグを立てる
        elif ((not self.check_all_black_line_flag) and line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.WHITE)):
            print("のった?")
            self.check_all_black_line_flag = True
            self.left_or_right = SteppingMotorMotion.RIGHTWARD
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
        # 黒い線かチェックするために左または右に少し進む
        elif (self.check_all_black_line_flag and self.execute_count<LR_STEP_TO_CHECK_ALL_BLACK_LINE):
            self.execute_count += 1
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.left_or_right)
        # 左または右に少し進み切ったら，チェックフラグをFalseにしてtrace_bitをONにする
        elif (self.check_all_black_line_flag and self.execute_count>=LR_STEP_TO_CHECK_ALL_BLACK_LINE):
            self.execute_count = 0
            self.check_all_black_line_flag = False
            self.left_or_right = SteppingMotorMotion.STOP
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
        # forward
        else:
            next_state = State.FREEBALL
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)

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
        # 閾値を超えたらLINETRACE -> next
        if self.all_black_line_count >= ALLBLACKLINE_COUNT_AND_NEXT[self.linetrace_next][0]:
            self.all_black_line_count = 0
            next_state = ALLBLACKLINE_COUNT_AND_NEXT[self.linetrace_next][1]
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 全部黒の線を超えたらカウントする
        elif (self.last_all_black_line_flag and line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK)):
            print("こえた")
            self.all_black_line_count += 1
            self.last_all_black_line_flag = False
            self.execute_count = 0
            self.check_all_black_line_flag = False
            self.left_or_right = SteppingMotorMotion.STOP
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 全部黒の線に乗ったら乗ったフラグを立てる
        elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
            print("のった")
            self.last_all_black_line_flag = True
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
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
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
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
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
        # 黒い線かチェックするために左または右に少し進む
        elif (self.check_all_black_line_flag and self.execute_count<self.instruction_steps[State.LINETRACE][0]):
            self.execute_count += 1
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
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
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # ライントレース
        else:
            next_state = State.LINETRACE
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(self.up_or_down)
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
            self.execute_count = 0
            next_state = State.DETECT
        else:
            # 左前進 (search内で履歴を遡る際の終了位置その1)
            if self.execute_count < self.instruction_steps[State.SEARCH][0]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.LEFTWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 前進
            elif self.execute_count < self.instruction_steps[State.SEARCH][1]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.his.append(SteppingMotorMotion.FORWARD)
                self.execute_count += 1
                next_state = State.SEARCH
            # 履歴を(search内で履歴を遡る際の終了位置その1)まで遡る
            elif self.execute_count < self.instruction_steps[State.SEARCH][2]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.execute_count += 1
                next_state = State.SEARCH
            # 前進(linetrace)
            elif self.execute_count < self.instruction_steps[State.SEARCH][3]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
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
            # 前進(linetrace)
            elif self.execute_count < self.instruction_steps[State.SEARCH][7]:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.execute_count += 1
                next_state = State.SEARCH
            # 実行回数を0まで戻し，探索済みの道番号を更新
            else:
                dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
                trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
                step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
                dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
                serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
                self.execute_count = 0
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
            self.execute_count = 0
            self.search_road_num = 0
            self.detect_missing_flag = False
        #　見失ったフラグがTrueで遡りきってない時DETECT中の履歴を遡る
        elif self.detect_missing_flag and len(self.his)!=0:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
            self.execute_count += 1
        #　見失ったフラグがTrueで遡りきったらDCモータを切りSEARCHに戻る
        elif self.detect_missing_flag and len(self.his)==0:
            next_state = State.SEARCH
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count = 0
            self.detect_missing_flag = False
        # ステッピングモータの履歴が長すぎたら見失ったフラグを立てる
        elif len(self.his) >= DETECT_HIS_LENGTH_LIMIT:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.detect_missing_flag = True
        # 右回転
        elif (x<X_MIN and dis < DETECTABLE_MAX_DIS):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
            self.his.append(SteppingMotorMotion.RIGHTWARD)
            self.execute_count += 1
            self.detect_missing_flag = False
        # 左回転
        elif (x>=X_MAX and dis < DETECTABLE_MAX_DIS):
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.his.append(SteppingMotorMotion.LEFTWARD)
            self.execute_count += 1
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
            self.execute_count += 1
            self.detect_missing_flag = False
        # forward
        else:
            next_state = State.DETECT
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.ON)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.his.append(SteppingMotorMotion.FORWARD)
            self.execute_count += 1

    
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
        # line trace
        if self.execute_count < self.instruction_steps[State.LOOKBACK][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.ON)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count += 1
            next_state = State.LOOKBACK
        # 180 lookback
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LOOKBACK)
            if self.now_obtain_color == 1:
                self.linetrace_next = AllBlackLineThres.TO_BLUE
            elif self.now_obtain_color == 2:
                self.linetrace_next = AllBlackLineThres.TO_YELLOW
            elif self.now_obtain_color == 3:
                self.linetrace_next = AllBlackLineThres.TO_RED
            self.up_or_down = ServoMotorMotion.UP
            next_state = State.LINETRACE

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit


    def goal(self) -> tuple[State, int, int, int, int, int]:
        """
        ゴールする

        Parameters
        ----------

        Returns
        -------
        """
        if self.execute_count < self.instruction_steps[State.GOAL][self.now_obtain_color][0][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.instruction_steps[State.GOAL][self.now_obtain_color][0][1])
            self.execute_count += 1
            next_state = State.GOAL
        # leftward90/forward
        elif self.execute_count < self.instruction_steps[State.GOAL][self.now_obtain_color][1][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.UP)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.instruction_steps[State.GOAL][self.now_obtain_color][1][1])
            self.execute_count += 1
            next_state = State.GOAL
        # サーボモータを下げる
        elif self.execute_count < self.instruction_steps[State.GOAL][self.now_obtain_color][2][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.instruction_steps[State.GOAL][self.now_obtain_color][2][1])
            self.execute_count += 1
            next_state = State.GOAL
        # rightback90/lookback
        elif self.execute_count < self.instruction_steps[State.GOAL][self.now_obtain_color][3][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.instruction_steps[State.GOAL][self.now_obtain_color][3][1])
            self.execute_count += 1
            next_state = State.GOAL
        # 待機/forward
        elif self.execute_count < self.instruction_steps[State.GOAL][self.now_obtain_color][4][0]:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(self.instruction_steps[State.GOAL][self.now_obtain_color][4][1])
            self.execute_count += 1
            next_state = State.GOAL
        else:
            dir_bit = decode_linetrace_direction_to_serial_data(LinetraceDirection.FOR)
            trace_bit = decode_linetrace_mode_to_serial_data(LinetraceMode.OFF)
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.OFF)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_count = 0
            if self.now_obtain_color == 1:
                self.linetrace_next = AllBlackLineThres.AFTER_BLUE
                self.all_black_line_count = 0
            elif self.now_obtain_color == 2:
                self.linetrace_next = AllBlackLineThres.AFTER_YELLOW
                self.all_black_line_count = 0
            elif self.now_obtain_color == 3:
                self.linetrace_next = AllBlackLineThres.AFTER_RED
                self.all_black_line_count = 1
            else:
                self.linetrace_next = AllBlackLineThres.TO_SEARCH

            self.now_obtain_color = 0
            self.up_or_down = ServoMotorMotion.DOWN
            next_state = State.LINETRACE

        return next_state, dir_bit, trace_bit, dc_bit, serv_bit, step_bit
