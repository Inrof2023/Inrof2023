from collections import deque
from utils import *
import time

# 吸引可能な領域のx座標の最小値
X_MIN = 100

# 吸引可能な領域のx座標の最大値
X_MAX = 220

# 吸引可能な領域のy座標の最小値
Y_MIN = 20

# 吸引可能な領域のy座標の最大値
Y_MAX = 230

# 球を吸引できる最大の距離
OBTAINABLE_MAX_DIS = 500

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


OBTAIN_STRUCTURE_STEP = [
    400,    #DC_STRUCTURE_STEPS
    400+300     #SERVO_STRUCTURE_STEPS
]

GOBACK_STRUCTURE_STEP = [
    20    #BACKWARD_STRUCTURE_STEPS
]

GOAL_STRUCTURE_STEP = [
    400,    #DC&SERVO_STRUCTURE_STEPS
]

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
        self.execute_instructure_count = 0
        self.start_t = 0

    def detect_all_black_line(self, left: int, center_left: int, center_right: int, right: int) -> None:
        line_sensor = LineSensor(left, center_left, center_right, right)
        # 全部黒の線に乗ったらフラグを立てる
        if ((not self.last_all_blak_line_flag) and (line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.last_all_blak_line_flag = True
        # 全部黒の線を超えたらカウントする
        elif ((self.last_all_blak_line_flag) and (line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.all_black_line_count += 1
            self.last_all_blak_line_flag = False
        return self.all_black_line_count

    def linetrace(self) -> tuple[State, int, int, int]:
        """
            ライントレースをしている
            Parameters
            ----------

            Returns
            -------
        """
        if self.execute_instructure_count == 0:
            next_state = State.LINETRACE
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 1
            self.start_t = time.time()
        elif time.time()-self.start_t < 5:
            next_state = State.LINETRACE
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
        elif time.time()-self.start_t < 10:
            next_state = State.LINETRACE
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        elif time.time()-self.start_t < 15:
            next_state = State.LINETRACE
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        else:
            next_state = State.LINETRACE
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.DOWN)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 0
        return next_state, dc_bit, serv_bit, step_bit