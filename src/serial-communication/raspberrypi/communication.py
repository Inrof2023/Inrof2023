import os
import serial
from typing import Tuple, Type
from enum import Enum
import unittest

def concatenate_bit_sequences(Direction: int ,LINETRACE: int ,DC_BIT: int, SERV_BIT: int, STEP_BIT: int) -> Type[bytes]:
    """
    それぞれのモータの制御ビットを結合して, そのバイト列（1byte）を返す
    上から3bitは0パディングしている
    
    Parameters
    ----------
    DC_BIT: int
        1bit
        DCモータの制御ビット
        0: 停止, 1: 動作
    
    SERV_BIT: int
        1bit
        サーボモータの制御ビット
        0: 停止, 1: 動作
    
    STEP_BIT: int
        3bit
        ステッピングモータの制御ビット
        000: 停止, 001: 前進, 010: 後退, 011: 左回転, 100: 右回転
        
    Returns
    -------
    Type[bytes]
        1byte
        それぞれのモータの制御ビットを結合したバイト列
    """
    # ビット列を結合
    byte =  Direction << 7 | LINETRACE << 6 | DC_BIT << 5 | SERV_BIT << 4 | STEP_BIT
    
    # バイト列に変換
    byte = byte.to_bytes(1, 'big')
    
    return byte

def communicate_with_arduino() -> None:
    """
    ardiunoとシリアル通信を行う
    """
    # シリアルポートを開く
    ser = serial.Serial(os.environ['SERIAL_PORT'], int(os.environ['BITRATE']))
    try:
        while True:
            # データを受信
            # left, center_left, center_right, right = ser.readline().decode('utf-8', 'ignore').split(",") #バイト列で受信
            serial_data = ser.readline().decode("utf-8", "ignore")
            print("デバッグ用：{}".format(serial_data))
            left, center_left, center_right, right = serial_data.split(",") #バイト列で受信
            print("photo lifter: {}, {}, {}, {}".format(left, center_left, center_right, right)) # デバッグ用
            
            # データを分ける
            # 4bitのデータ（０, 1の文字列）を受信する, カンマ区切り
            
            # 色々処理する
            
            # データをビット列に変換
            # 仮置き
            ###################
            Direction = 0b0
            LineTrace = 0b0
            DC_BIT = 0b0
            SERV_BIT = 0b0
            STEP_BIT = 0b0001
            ###################
            # STEP_BIT = determine_robot_motion_from_photoreflector(int(left), int(center_left), int(center_right), int(right))
            
            serial_byte = concatenate_bit_sequences(Direction, LineTrace, DC_BIT, SERV_BIT, STEP_BIT)
            
            # print(serial_byte)
            
            # データを送信
            ser.write(serial_byte)
            
            ser.flush()
            
            # デバッグ用
             # print("send: {}".format(ser.readline()))
    except:
        # 停止
        Direction = 0b0
        LineTrace = 0b0
        DC_BIT = 0b0
        SERV_BIT = 0b0
        STEP_BIT = 0b0000
        serial_byte = concatenate_bit_sequences(Direction, LineTrace, DC_BIT, SERV_BIT, STEP_BIT)
        
        ser.write(serial_byte)
        ser.flush()

# フォトリフテクタの閾値
THRESHOLD: int = 500

class LineType(Enum):
    """
    ラインの種類を表す
    """
    WHITE = 0,
    BLACK = 1,
    
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
        __value : Tuple[LineType, LineType, LineType, LineType
            フォトリフレクタの値
            
        Returns
        -------
        bool
            フォトリフレクタの値が等しいかどうか
        """
        return self.left == __value[0] and self.center_left == __value[1] and self.center_right == __value[2] and self.right == __value[3]

def determine_robot_motion_from_photoreflector(left: int, center_left: int, center_right: int, right:int) -> int:
    """
    ロボットの動きをフォトリフレクタの値から決定する
    
    Parameters
    ----------
    left : int
    center_left : int
    center_right : int
    right : int
    
    Returns
    -------
    int :
        ロボットの動きを表すビット列
    """
    
    line_sensor = LineSensor(left, center_left, center_right, right)
    
    # フォトリフレクタの値から進む方向を決定
    # とりあえず全パターンを列挙
    
    if line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.WHITE):
        return decode_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.WHITE):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.WHITE):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.WHITE):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.BLACK):
        return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.BLACK):
        return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    else:
        return 0b000
    
    # if line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.WHITE):
    #     # to do
    #     # https://github.com/Inrof2023/Inrof2023/issues/45
    #     return 0b000
    # elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.WHITE, LineType.BLACK):
    #     return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    # elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    # elif line_sensor == (LineType.WHITE, LineType.WHITE, LineType.BLACK, LineType.BLACK):
    #     return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    # elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    # elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.WHITE, LineType.BLACK):
    #     # ありえないパターン
    #     return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    # elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.WHITE, LineType.BLACK, LineType.BLACK, LineType.BLACK):
    #     return decode_to_serial_data(SteppingMotorMotion.LEFTWARD)
    # elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    # elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.WHITE, LineType.BLACK):
    #     # 考えなくていいケース
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.WHITE):
    #     # 考えなくていいケース
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.BLACK, LineType.WHITE, LineType.BLACK, LineType.BLACK):
    #     # 考えなくていいケース
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.RIGHTWARD)
    # elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.WHITE, LineType.BLACK):
    #     # 考えなくていいケース
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.WHITE):
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    # elif line_sensor == (LineType.BLACK, LineType.BLACK, LineType.BLACK, LineType.BLACK):
    #     return decode_to_serial_data(SteppingMotorMotion.FORWARD)
    
    # arduinoへそのデータを送信する
    
    return

def decode_to_serial_data(stepping_motor_motion: SteppingMotorMotion) -> int:
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
    

def determine_robot_motion_from_camera() -> None:
    """
    ロボットの動きをカメラの値から決定する
    ラインから外れてボールを拾いに行くときに使う
    
    Parameters
    ----------
    
    Returns
    -------
    """
    return

#テスト用のクラス
class TestCommunication(unittest.TestCase):
    def test_concatenate_bit_sequences(self):
        DC_BIT = 0b1
        SERV_BIT = 0b1
        SETP_BIT = 0b100
        
        byte = concatenate_bit_sequences(DC_BIT, SERV_BIT, SETP_BIT)
        
        self.assertEqual(byte, b'\x1c')
        
        return

if __name__ == '__main__':
    # シリアル通信用のポートを環境変数に設定
    # os.environ['SERIAL_PORT'] = '/dev/ttyUSB0'
    os.environ['SERIAL_PORT'] = '/dev/tty.usbserial-110'
    os.environ['BITRATE'] = '9600'
    
    # 単体テスト
    # unittest.main()
    
    communicate_with_arduino()