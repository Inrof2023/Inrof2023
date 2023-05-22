import os
import serial
from typing import Tuple, Type
import unittest

def concatenate_bit_sequences(DC_BIT: int, SERV_BIT: int, STEP_BIT: int) -> Type[bytes]:
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
    byte = DC_BIT << 4 | SERV_BIT << 3 | STEP_BIT
    
    # バイト列に変換
    byte = byte.to_bytes(1, 'big')
    
    return byte

def communicate_with_arduino() -> None:
    """
    ardiunoとシリアル通信を行う
    """
    # シリアルポートを開く
    ser = serial.Serial(os.environ['SERIAL_PORT'], int(os.environ['BITRATE']))
    
    while True:
        # データを受信
        left, center_left, center_right, right = ser.readline().decode('utf-8', 'ignore').split(",") #バイト列で受信
        print("photo lifter: {}, {}, {}, {}".format(left, center_left, center_right, right)) # デバッグ用
        
        # データを分ける
        # 4bitのデータ（０, 1の文字列）を受信する, カンマ区切り
        
        # 色々処理する
        
        # データをビット列に変換
        # 仮置き
        ###################
        DC_BIT = 0b1
        SERV_BIT = 0b1
        STEP_BIT = 0b001
        ###################
        serial_byte = concatenate_bit_sequences(DC_BIT, SERV_BIT, STEP_BIT)
        
        # データを送信
        ser.write(serial_byte)
        
        # デバッグ用
        # print("send: {}".format(ser.readline()))
        
    return

def determine_robot_motion_from_photoreflector(left: float, center_left: float, center_right: float, right:float) -> None:
    """
    ロボットの動きをフォトリフレクタの値から決定する
    
    Parameters
    ----------
    left : float
    center_left : float
    center_right : float
    right : float
    
    Returns
    -------
    None
    """
    return

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