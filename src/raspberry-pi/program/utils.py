from typing import Tuple, Type
from enum import Enum

# フォトリフレクタの閾値
THRESHOLD = 400

class State(Enum):
    """
    ロボットの状態を表す
    """
    LINETRACE = 0,
    SEARCH = 1,
    DETECT = 2,
    OBTAIN = 3,
    REDO = 4,
    GOBACK = 5,
    GOAL = 6,

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
    OFF = 0b0,
    ON = 0b1,

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
    if servo_motor_motion == ServoMotorMotion.OFF:
        return 0b0
    elif servo_motor_motion == ServoMotorMotion.ON:
        return 0b1
