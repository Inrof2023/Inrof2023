from camera import Camera
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
    STOP = 0b000,
    FORWARD = 0b001,
    BACKWARD = 0b010,
    LEFTWARD = 0b011,
    RIGHTWARD = 0b100,
    LEFTBACK = 0b101,
    RIGHTBACK = 0b110,

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
        pass
    
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


def search(cam_data :tuple[int, int, int, int], ard_data :tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """
        フォトリフレクタの値からモータ―の動きを決める
        カメラとボールの距離から次の状態を決める

        Parameters
        ----------
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
        next_state : int
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
    left, center_left, center_right, right = ard_data
    line_sensor = LineSensor(left, center_left, center_right, right)
    _, _, dis, _ = cam_data

    # ボールを発見したらsearch -> detect
    if (dis < DETECTABLE_MAX_DIS):
        next_state = decode_state_to_int(State.DETECT)
    else:
        next_state = decode_state_to_int(State.SEARCH)

    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)

    # フォトリフレクタの値から進む方向を決定
    # とりあえず全パターンを列挙
    
    if line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.WHITE):
        # to do
        # https://github.com/Inrof2023/Inrof2023/issues/45
        step_bit = 0b000
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.BLACK):
        # ありえないパターン
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.WHITE):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.FORWARD)
    return next_state, dc_bit, serv_bit, step_bit

def detect(cam_data  :tuple[int, int, int, int], his :Deque) -> tuple[int, int, int, int]:
    """
    カメラの値からモータ―の動きを決める
    ステッピングモータの履歴を保存する

    Parameters
    ----------
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

    his : Deque
        ステッピングモータの履歴を管理するキュー

    Returns
    -------
    next_state : int
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
    000: 停止, 001: 前進, 010: 後退, 011: 左回転, 100: 右回転　101: 左後回転, 110: 右後回転
    """
    x, y, dis, col = cam_data

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
    next_state : int
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
    his : Deque
        ステッピングモータの履歴を管理するキュー

    Returns
    -------
    next_state : int
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


def goback(ard_data :tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """
        フォトリフレクタの値からモータ―の動きを決める

        Parameters
        ----------
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
    left, center_left, center_right, right = ard_data
    line_sensor = LineSensor(left, center_left, center_right, right)

    next_state = decode_state_to_int(State.SEARCH)
    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.RUN)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.RUN)

    if line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.WHITE):
        # to do
        # https://github.com/Inrof2023/Inrof2023/issues/45
        step_bit = 0b000
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTBACK)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.BLACK):
        # ありえないパターン
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.LEFTBACK)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTBACK)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.WHITE):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.RIGHTBACK)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.BLACK):
        # 考えなくていいケース
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.WHITE):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
        step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.BACKWARD)
    return next_state, dc_bit, serv_bit, step_bit

def goal():
    """
    ゴールする

    Parameters
    ----------

    Returns
    -------
    next_state : int
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
    next_state = decode_state_to_int(State.SEARCH)
    dc_bit = decode_dc_motor_motion_to_serial_data(DCMotorMotion.STOP)
    serv_bit = decode_servo_motor_motion_to_serial_data(ServoMotorMotion.STOP)
    step_bit = decode_stepping_motor_motion_to_serial_data(SteppingMotorMotion.STOP)
    return next_state, dc_bit, serv_bit, step_bit

def decode_stepping_motor_motion_to_serial_data(stepping_motor_motion: SteppingMotorMotion) -> int:
    if stepping_motor_motion == SteppingMotorMotion.STOP:
        return 0b000
    elif stepping_motor_motion == SteppingMotorMotion.FORWARD:
        return 0b001
    elif stepping_motor_motion == SteppingMotorMotion.BACKWARD:
        return 0b010
    elif stepping_motor_motion == SteppingMotorMotion.LEFTWARD:
        return 0b011
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTWARD:
        return 0b100
    elif stepping_motor_motion == SteppingMotorMotion.LEFTBACK:
        return 0b101
    elif stepping_motor_motion == SteppingMotorMotion.RIGHTBACK:
        return 0b110

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

