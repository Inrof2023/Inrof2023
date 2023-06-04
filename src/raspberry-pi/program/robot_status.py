from collections import deque
from utils import *


# 吸引可能な領域のx座標の最v小値
X_MIN = 10

# 吸引可能な領域のx座標の最大値
X_MAX = 90

# 吸引可能な領域のy座標の最小値
Y_MIN = 100

# 吸引可能な領域のy座標の最大値
Y_MAX = 140

# 球を吸引できる最大の距離
OBTAINABLE_MAX_DIS = 180

# 球を検出できる最大の距離
DETECTABLE_MAX_DIS = 1000

# サーボを動かす時間
SERV_TIMEOUT = 3

# ボールがあるエリアにいるかを，全部黒いラインを超えた回数で認識する
ALL_BLACK_LINE_COUNT_READY_TO_SEARCH = 4

# 赤にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_RED_GOAL = 4

# 青にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_BLUE_GOAL = 3

# 黄にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_YELLOW_GOAL = 3

# 180度旋回時のループ数
ROTATE_LOOP_TIMES = 1

# ゴール後の前進のループ数
LITTLE_FORWARD_LOOP_TIMES = 1

# 左回転のループ数
LEFTWARD_LOOP_TIMES = 1

# 左後ろ回転のループ数
LEFTBACK_LOOP_TIMES = 1

# 青ゴール時に用いる直進時のループ数
STRAIGHT_BLUE_LOOP_TIMES = 1

# サーボモータを駆動時のループ数
SERVO_LOOP_TIMES = 1

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

    def detect_all_black_line(self, left: int, center_left: int, center_right: int, right: int) -> None:
        line_sensor = LineSensor(left, center_left, center_right, right)
        # 全部黒の線に乗ったらフラグを立てる
        if ((not self.last_all_blak_line_flag) and (line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.last_all_blak_line_flag = True
        # 全部黒の線を超えたらカウントする
        elif ((self.last_all_blak_line_flag) and (line_sensor != (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK))):
            self.all_black_line_count += 1
            self.last_all_blak_line_flag = False

    def linetrace(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int]:
        """
            ライントレースをしている
            Parameters
            ----------

            Returns
            -------
        """
        self.detect_all_black_line(left, center_left, center_right, right)
        # ボールのあるエリアに着いたらlinetrace -> search
        if (self.all_black_line_count >= ALL_BLACK_LINE_COUNT_READY_TO_SEARCH):
            next_state = State.SEARCH
        else:
            next_state = State.LINETRACE

        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
        step_bit = 0b0000
        return next_state, dc_bit, serv_bit, step_bit

    def search(self, dis: int) -> tuple[State, int, int, int]:
        """
            ボールを探している
            Parameters
            ----------

            Returns
            -------
        """
        # 検出可能距離以内にボールを発見したらsearch -> detect
        if (dis < DETECTABLE_MAX_DIS):
            next_state = State.DETECT
        else:
            next_state = State.SEARCH

        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
        step_bit = 0b0000
        return next_state, dc_bit, serv_bit, step_bit

    def detect(self, x: int, y: int, dis: int, col: int) -> tuple[State, int, int, int]:
        """
        カメラの値からモータ―の動きを決める
        ステッピングモータの履歴を保存する

        Parameters
        ----------

        Returns
        -------
        """

        # ボールの検出可能範囲から外れたら全モータを停止してsearchに戻る
        # また，ステッピングモータの履歴をリセットする
        if (dis>=DETECTABLE_MAX_DIS):
            next_state = State.SEARCH
            self.his.clear()
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            return next_state, dc_bit, serv_bit, step_bit
        # カメラを左に90度傾けているため座標に注意
        # 左回転
        elif (y<Y_MIN):
            next_state = State.DETECT
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.his.append(SteppingMotorMotion.LEFTWARD)
        # 右回転
        elif (y>Y_MAX):
            next_state = State.DETECT
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
            self.his.append(SteppingMotorMotion.RIGHTWARD)
        # 範囲内にボールが来ていれば停止してdetect -> obtain
        elif (x>X_MIN and x<X_MAX and y>Y_MIN and y<Y_MAX and dis<OBTAINABLE_MAX_DIS):
            self.now_obtain_color = col
            self.all_black_line_count = 0
            next_state = State.OBTAIN
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        # 前進
        else:
            next_state = State.DETECT
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.his.append(SteppingMotorMotion.FORWARD)
    
        return next_state, dc_bit, serv_bit, step_bit

    def obtain(self) -> tuple[State, int, int, int]:
        """
        DCモータとサーボモータを動かす

        Parameters
        ----------

        Returns
        -------
        """

        next_state = State.REDO
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        return next_state, dc_bit, serv_bit, step_bit

    def redo(self) -> tuple[State, int, int, int]:
        """
        detect状態の時のモータの値を遡る

        Parameters
        ----------

        Returns
        -------
        """
        
        if len(self.his) != 0:
            next_state = State.REDO
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(self.his.pop()))
        elif self.execute_instructure_count<ROTATE_LOOP_TIMES:
            next_state = State.REDO
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTROTATE)
            self.execute_instructure_count += 1
        else:
            next_state = State.GOBACK
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 0
            
        return next_state, dc_bit, serv_bit, step_bit


    def goback(self, left: int, center_left: int, center_right: int, right: int) -> tuple[State, int, int, int]:
        """
            逆走でライントレースを行っている

            Parameters
            ----------

            Returns
            -------
        
        """
        
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
        step_bit = 0b0000
        self.detect_all_black_line(left, center_left, center_right, right)
        # 赤の時
        if self.now_obtain_color == 0 and self.all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_RED_GOAL:
            self.all_black_line_count = 1
            next_state = State.GOAL
        # 青の時
        elif self.now_obtain_color == 1 and self.all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_BLUE_GOAL:
            self.all_black_line_count = 2
            next_state = State.GOAL
        # 黄の時
        elif self.now_obtain_color == 2 and self.all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_YELLOW_GOAL:
            self.all_black_line_count = 2
            next_state = State.GOAL
        else:
            next_state = State.GOBACK
    
        return next_state, dc_bit, serv_bit, step_bit

    def goal_red(self) -> tuple[State, int, int, int]:
        """
        赤のボールをゴールする

        Parameters
        ----------

        Returns
        -------
    
        """
        # 左回転
        if self.execute_instructure_count < LEFTWARD_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ゴールに入れる
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 左後ろ回転
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES+LEFTBACK_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 少し前進
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES+LEFTBACK_LOOP_TIMES+LITTLE_FORWARD_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ライントレースに移行
        else:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 0
            next_state = State.LINETRACE
        return next_state, dc_bit, serv_bit, step_bit

    def goal_blue(self) -> tuple[State, int, int, int]:
        """
        青のボールをゴールする

        Parameters
        ----------

        Returns
        -------
    
        """
        # 黄ゴール前から青ゴール前まで直進
        if self.execute_instructure_count <  STRAIGHT_BLUE_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 左回転
        if self.execute_instructure_count < STRAIGHT_BLUE_LOOP_TIMES+LEFTWARD_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ゴールに入れる
        elif self.execute_instructure_count <  STRAIGHT_BLUE_LOOP_TIMES+LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 左後ろ回転
        elif self.execute_instructure_count <  STRAIGHT_BLUE_LOOP_TIMES+LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES+LEFTBACK_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ライントレースに移行
        else:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 0
            next_state = State.LINETRACE
        return next_state, dc_bit, serv_bit, step_bit

    def goal_yellow(self) -> tuple[State, int, int, int]:
        """
        黄のボールをゴールする

        Parameters
        ----------

        Returns
        -------
    
        """
        # 左回転
        if self.execute_instructure_count < LEFTWARD_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.ON)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ゴールに入れる
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 左後ろ回転
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES+LEFTBACK_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # 少し前進
        elif self.execute_instructure_count <  LEFTWARD_LOOP_TIMES+SERVO_LOOP_TIMES+LEFTBACK_LOOP_TIMES+LITTLE_FORWARD_LOOP_TIMES:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
            self.execute_instructure_count += 1
            next_state = State.GOAL
        # ライントレースに移行
        else:
            dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
            serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.OFF)
            step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
            self.execute_instructure_count = 0
            next_state = State.LINETRACE
        return next_state, dc_bit, serv_bit, step_bit

