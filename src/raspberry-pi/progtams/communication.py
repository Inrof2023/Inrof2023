import numpy as np
import time
import os
import serial
from typing import Type
from controller import Controller

# 決勝の競技時間+準備時間(12分)×トライ可能数(4回)×60秒
GAMETIME = 2880

class Communication:
    def __init__(self):
        # シリアル通信用のポートを環境変数に設定
        #os.environ['SERIAL_PORT'] = '/dev/ttyUSB0'
        os.environ['SERIAL_PORT'] = 'COM5'
        os.environ['BITRATE'] = '9600'
        self.ser = serial.Serial(os.environ['SERIAL_PORT'], int(os.environ['BITRATE']))
        self.ctrl = Controller()
        self.ard_data = 0,0,0,0
        self.serial_byte = 0b0, 0b0, 0b000

    def concatenate_bit_sequences(self, DC_BIT: int, SERV_BIT: int, STEP_BIT: int) -> Type[bytes]:
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
            000: 停止, 001: 前進, 010: 後退, 011: 左回転, 100: 右回転　101: 左後回転, 110: 右後回転
        
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

    def test(self) -> None:
        """
        PCとカメラでテスト
        """
        start_time = time.time()
        while (time.time()-start_time<GAMETIME):
            left, center_left, center_right, right = 10, 10, 10, 10

            self.ard_data = left, center_left, center_right, right
            DC_BIT, SERV_BIT, STEP_BIT = self.ctrl.controller(self.ard_data)
            self.serial_byte = self.concatenate_bit_sequences(DC_BIT, SERV_BIT, STEP_BIT)

            print("left, center_left, center_right, right : ", left, center_left, center_right, right)
            print("next_state_num", self.ctrl.next_state_num)
            print("DC_BIT, SERV_BIT, STEP_BIT", DC_BIT, SERV_BIT, STEP_BIT)
            print("serial_byte : ", self.serial_byte)
            os.system('cls')

    def communicate(self) -> None:
        """
        ArduinoとRaspberry Piでシリアル通信
        """
        start_time = time.time()
        while (time.time()-start_time<GAMETIME):
            # データを受信
            # データを分ける
            # 4bitのデータ（０, 1の文字列）を受信する, カンマ区切り
            try:
                left, center_left, center_right, right = self.ser.readline().decode('utf-8', 'ignore').split(",") #バイト列で受信
            except ValueError:
                continue

            self.ard_data = int(left), int(center_left), int(center_right), int(right)
            DC_BIT, SERV_BIT, STEP_BIT = self.ctrl.controller(self.ard_data)
            #self.serial_byte = self.concatenate_bit_sequences(DC_BIT, SERV_BIT, STEP_BIT)
            self.serial_byte = self.concatenate_bit_sequences(0b0, 0b0, STEP_BIT)

            print("left, center_left, center_right, right : ", left, center_left, center_right, right)
            print("next_state_num", self.ctrl.next_state_num)
            print("DC_BIT, SERV_BIT, STEP_BIT", DC_BIT, SERV_BIT, STEP_BIT)
            # print("serial_byte : ", self.serial_byte)
            #os.system('cls')
        
            # データを送信
            self.ser.write(self.serial_byte)

if __name__ == "__main__":
    com = Communication()

    # テスト
    # com.test()

    # 通信
    com.communicate()


