import os
import serial
from typing import Tuple

def communicate_with_arduino() -> None:
    """
    ardiunoとシリアル通信を行う
    """
    # シリアルポートを開く
    ser = serial.Serial(os.environ['SERIAL_PORT'], os.environ['BITRATE'])
    
    while True:
        # データを受信
        string_data = ser.readline().split(",")
        
        # データを分ける
        # 4bitのデータ（０, 1の文字列）を受信する, カンマ区切り
        
        # 色々処理する
        
        # データを送信
        #ser.write()
        
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

if __name__ == '__main__':
    # シリアル通信用のポートを環境変数に設定
    os.environ['SERIAL_PORT'] = '/dev/ttyUSB0'
    os.environ['BITRATE'] = 115200