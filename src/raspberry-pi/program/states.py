from collections import deque
from typing import Tuple, Type, Deque
from enum import Enum

# フォトリフレクタの閾値
THRESHOLD = 400

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

# 赤にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_RED_GOAL = 4

# 青にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_BLUE_GOAL = 2

# 黄にゴールするために，全部黒いラインを超えた回数を認識する
ALL_BLACK_LINE_COUNT_FOR_YELLOW_GOAL = 3

class State(Enum):
    """
    ロボットの状態を表す
    """
    SEARCH = 0,
    DETECT = 1,
    OBTAIN = 2,
    REDO = 3,
    GOBACK = 4,
    GOAL = 5,

class SteppingMotorMotion(Enum):
    """
    左右のステッピングモータの動きを表す
    """
    STOP = 0b0000,
    FORWARD = 0b0001,
    BACKWARD = 0b0010,
    LEFTWARD = 0b0011,
    RIGHTWARD = 0b0100,
    LEFTBACK = 0b0101,
    RIGHTBACK = 0b0110,
    LEFTROTATE = 0b0111,
    RIGHTROTATE = 0b1000,

class DCMotorMotion(Enum):
    """
    DCモータの動きを表す
    """
    STOP = 0b0,
    RUN = 0b1,

class ServoMotorMotion(Enum):
    """
    サーボモータの動きを表す
    """
    STOP = 0b0,
    RUN = 0b1,

class LineType(Enum):
    """
    ラインの種類を表す
    """
    WHITE = 0,
    BLACK = 1,

class LineSensor:
    """
    ラインセンサの値を表す
    
    Attributes
    ----------
    left : Type[LineType]
        左のセンサの白黒
    center_left : Type[LineType]
        左中央の白黒
    center_right : Type[LineType]
        右中央の白黒
    right : Type[LineType]
        右のセンサの白黒
    
    Parameters
    ----------
    left : int
        左のセンサの値
    center_left : int
        左中央のセンサの値
    center_right : int
        右中央のセンサの値
    right : int
        右のセンサの値
    """
    def __init__(self, left: int, center_left: int, center_right: int, right: int) -> None:
        self.left = self.set_color_type(left)
        self.center_left = self.set_color_type(center_left)
        self.center_right = self.set_color_type(center_right)
        self.right = self.set_color_type(right)
    
    def set_color_type(self, photo_reflector_value: int) -> Type[LineType]:
        """
        フォトリフレクタの値からラインの色を判定する
        
        Parameters
        ----------
        photo_reflector_value : int
            フォトリフレクタの値
        
        Returns
        -------
        Type[LineType]
            ラインの色を表す列挙型
        """
        if photo_reflector_value > THRESHOLD:
            return LineType.WHITE
        else:
            return LineType.BLACK
        
    def __eq__(self, __value: Tuple[LineType, LineType, LineType, LineType]) -> bool:
        """
        フォトリフレクタの値が等しいかどうかを判定する
        LineSensorのインスタンスと==で比較できる
        
        Parameters
        ----------
        __value : Tuple[LineType, LineType, LineType, LineType]
            フォトリフレクタの値
            
        Returns
        -------
        bool
            フォトリフレクタの値が等しいかどうか
        """
        return self.left == __value[0] and self.center_left == __value[1] and self.center_right == __value[2] and self.right == __value[3]


def search(dis: int, isdDetectable: bool) -> tuple[int, int, int, int]:
    """
        ライントレースを行っている
        Parameters
        ----------

        Returns
        -------
    """
    # ボールのあるエリアについて，検出可能距離以内にボールを発見したらsearch -> detect
    if (isDetectable and dis < DETECTABLE_MAX_DIS):
        next_state = decode_state_to_int(State.DETECT)
    else:
        next_state = decode_state_to_int(State.SEARCH)


    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
    step_bit = 0b0000
    return next_state, dc_bit, serv_bit, step_bit

def detect(x: int, y: int, dis: int, his :Deque) -> tuple[int, int, int, int]:
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
        next_state = decode_state_to_int(State.SEARCH)
        his.clear()
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
        return next_state, dc_bit, serv_bit, step_bit
    # カメラを左に90度傾けているため座標に注意
    # 左回転
    elif (y<Y_MIN):
        next_state = decode_state_to_int(State.DETECT)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
        his.append(SteppingMotorMotion.LEFTWARD)
    # 右回転
    elif (y>Y_MAX):
        next_state = decode_state_to_int(State.DETECT)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
        his.append(SteppingMotorMotion.RIGHTWARD)
    # 範囲内にボールが来ていれば停止してdetect -> obtain
    elif (x>X_MIN and x<X_MAX and y>Y_MIN and y<Y_MAX and dis<OBTAINABLE_MAX_DIS):
        next_state = decode_state_to_int(State.OBTAIN)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
    # 前進
    else:
        next_state = decode_state_to_int(State.DETECT)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
        his.append(SteppingMotorMotion.FORWARD)
    
    return next_state, dc_bit, serv_bit, step_bit

def obtain():
    """
    DCモータとサーボモータを動かす

    Parameters
    ----------

    Returns
    -------
    """
    next_state = decode_state_to_int(State.REDO)
    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.RUN)
    step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
    return next_state, dc_bit, serv_bit, step_bit

def redo(his :Deque) -> tuple[int, int, int, int]:
    """
    detect状態の時のモータの値を遡る

    Parameters
    ----------

    Returns
    -------
    """
    if len(his) == 0:
        next_state = decode_state_to_int(State.GOBACK)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.RUN)
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
    else:
        next_state = decode_state_to_int(State.REDO)
        dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
        serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.RUN)
        step_bit = decode_stepping_motor_motion_to_serial_data(reverse_stepping_motor_motion(his.pop()))
    return next_state, dc_bit, serv_bit, step_bit


def goback(now_obtain_color: int, all_black_line_count: int, left: int, center_left: int, center_right: int, right: int) -> tuple[int, int, int, int]:
    """
        フォトリフレクタの値からモータ―の動きを決める

        Parameters
        ----------

        Returns
        -------
        
    """
    line_sensor = LineSensor(left, center_left, center_right, right)
    # 赤の時
    if now_obtain_color == 0 and all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_RED_GOAL:
        next_state = decode_state_to_int(State.GOAL)
    
    # 青の時
    elif now_obtain_color == 1 and all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_BLUE_GOAL:
        next_state = decode_state_to_int(State.GOAL)
    
    # 黄の時
    elif now_obtain_color == 2 and all_black_line_count == ALL_BLACK_LINE_COUNT_FOR_YELLOW_GOAL:
        next_state = decode_state_to_int(State.GOAL)

    else:
        next_state = decode_state_to_int(State.GOBACK)
    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.RUN)
    step_bit = 0b0000
    
    return next_state, dc_bit, serv_bit, step_bit

def goal():
    """
    ゴールする

    Parameters
    ----------

    Returns
    -------
    
    """
    next_state = decode_state_to_int(State.SEARCH)
    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
    step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
    return next_state, dc_bit, serv_bit, step_bit

def decode_stepping_motor_motion_to_serial_data(stepping_motor_motion: SteppingMotorMotion) -> int:
    if stepping_motor_motion == SteppingMotorMotion.STOP:
        return 0b0000
    elif stepping_motor_motion == SteppingMotorMotion.FORWARD:
        return 0b0001
    elif stepping_motor_motion == SteppingMotorMotion.BACKWARD:
        return 0b0010
    elif stepping_motor_motion == SteppingMotorMotion.LEFTWARD:
        return 0b0011
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTWARD:
        return 0b0100
    elif stepping_motor_motion == SteppingMotorMotion.LEFTBACK:
        return 0b0101
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTBACK:
        return 0b0110
    elif stepping_motor_motion == SteppingMotorMotion.LEFTROTATE:
        return 0b0111
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTROTATE:
        return 0b1000

def reverse_stepping_motor_motion(stepping_motor_motion: SteppingMotorMotion) -> SteppingMotorMotion:
    if stepping_motor_motion == SteppingMotorMotion.STOP:
        return SteppingMotorMotion.STOP
    elif stepping_motor_motion == SteppingMotorMotion.FORWARD:
        return SteppingMotorMotion.BACKWARD
    elif stepping_motor_motion == SteppingMotorMotion.BACKWARD:
        return SteppingMotorMotion.FORWARD
    elif stepping_motor_motion == SteppingMotorMotion.LEFTWARD:
        return SteppingMotorMotion.LEFTBACK
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTWARD:
        return SteppingMotorMotion.RIGHTBACK
    elif stepping_motor_motion == SteppingMotorMotion.LEFTBACK:
        return SteppingMotorMotion.LEFTWARD
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTBACK:
        return SteppingMotorMotion.RIGHTWARD
    else:
        return SteppingMotorMotion.STOP

def decode_dc_motor_motion_to_serial_data(dc_motor_motion: DCMotorMotion) -> int:
    if dc_motor_motion == DCMotorMotion.STOP:
        return 0b0
    elif dc_motor_motion == DCMotorMotion.RUN:
        return 0b1

def decode_servo_motor_motion_to_serial_data(servo_motor_motion: ServoMotorMotion) -> int:
    if servo_motor_motion == ServoMotorMotion.STOP:
        return 0b0
    elif servo_motor_motion == ServoMotorMotion.RUN:
        return 0b1

def decode_state_to_int(state: State) -> int:
    if state == State.SEARCH:
        return 0
    elif state == State.DETECT:
        return 1
    elif state == State.OBTAIN:
        return 2
    elif state == State.REDO:
        return 3
    elif state == State.GOBACK:
        return 4
    elif state == State.GOAL:
        return 5
