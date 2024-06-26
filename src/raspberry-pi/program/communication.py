from pickle import FALSE
import numpy as np
import time
import os
import serial
from typing import Type
from controller import Controller
from utils import *

# 決勝の競技時間+準備時間(12分)×トライ可能数(4回)×60秒
GAMETIME = 2880

class Communication:
    def __init__(self):
        # シリアル通信用のポートを環境変数に設定
        os.environ['SERIAL_PORT'] = '/dev/ttyUSB0'
        #os.environ['SERIAL_PORT'] = 'COM4'
        os.environ['BITRATE'] = '9600'
        self.ser = serial.Serial(os.environ['SERIAL_PORT'], int(os.environ['BITRATE']))
        self.ctrl = Controller()
        self.serial_byte = 0b0, 0b0, 0b0, 0b0, 0b0000

    def concatenate_bit_sequences(self, DIR_BIT: int, TRACE_BIT: int, DC_BIT: int, SERV_BIT: int, STEP_BIT: int) -> Type[bytes]:
        """
        それぞれのモータの制御ビットを結合して, そのバイト列（1byte）を返す
    
        Parameters
        ----------
        DIR_BIT: int
            1bit
            ライントレースをする時の向き
            0: 前進, 1: 後進

        TRACE_BIT: int
            1bit
            ライントレースをするかどうか
            0: ライントレースしない(Raspberry Piが制御), 1: ライントレースする(Arduinoが制御)

        DC_BIT: int
            1bit
            DCモータの制御ビット
            0: 停止, 1: 動作
    
        SERV_BIT: int
            1bit
            サーボモータの制御ビット
            0: 停止, 1: 動作
    
        STEP_BIT: int
            4bit
            ステッピングモータの制御ビット
            0000: 停止, 0001: 前進, 0010: 後退, 0011: 左回し, 0100: 右回し　0101: 左後ろ回し, 0110: 右後ろ回し, 
            0111: 左90回し, 1000: 右90回し, 1001: 左後ろ90回し, 1010: 右後ろ90回し, 1011: 方向転換
        
        Returns
        -------
        Type[bytes]
            1byte
            それぞれのモータの制御ビットを結合したバイト列
        """
        # ビット列を結合
        byte = DIR_BIT << 7 | TRACE_BIT << 6 | DC_BIT << 5 | SERV_BIT << 4 | STEP_BIT
    
        # バイト列に変換
        byte = byte.to_bytes(1, 'big')
    
        return byte

    def test(self) -> None:
        """
        PCとカメラでテスト
        """
        start_time = time.time()
        while (time.time()-start_time<GAMETIME):
            if(int(time.time()-start_time)%5==0):
                left, center_left, center_right, right = 10, 10, 10, 10
            else:
                left, center_left, center_right, right = 10, 10, 10, 1000
            

            DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT = self.ctrl.controller(left, center_left, center_right, right)
            self.serial_byte = self.concatenate_bit_sequences(DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT)
            print("left, center_left, center_right, right : ", int(left), int(center_left), int(center_right), int(right))
            print("DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT : ", DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT)
            print("serial_byte : ", self.serial_byte)
            print("next_state : ", self.ctrl.next_state)
            print("now_obtain_color : ", self.ctrl.rbst.now_obtain_color)
            print("last_all_black_line_flag : ", self.ctrl.rbst.last_all_black_line_flag)
            print("all_black_line_count : ", self.ctrl.rbst.all_black_line_count)
            print("check_all_black_line_flag : ",self.ctrl.rbst.check_all_black_line_flag)
            print("left_or_right : ", self.ctrl.rbst.left_or_right)
            print("execute_count : ", self.ctrl.rbst.execute_count)
            print("search_his_length : ", self.ctrl.rbst.search_his_length)
            print("len(his) : ", len(self.ctrl.rbst.his))
            print("**************************************************")
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
                left, center_left, center_right, right = int(left), int(center_left), int(center_right), int(right)
            except ValueError as e:
                print(e)
                continue

            DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT = self.ctrl.controller(left, center_left, center_right, right)
            self.serial_byte = self.concatenate_bit_sequences(DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT)
            
            print("left, center_left, center_right, right : ", int(left), int(center_left), int(center_right), int(right))
            print("DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT : ", DIR_BIT, TRACE_BIT, DC_BIT, SERV_BIT, STEP_BIT)
            print("serial_byte : ", self.serial_byte)
            print("next_state : ", self.ctrl.next_state)
            print("now_obtain_color : ", self.ctrl.rbst.now_obtain_color)
            print("last_all_black_line_flag : ", self.ctrl.rbst.last_all_black_line_flag)
            print("all_black_line_count : ", self.ctrl.rbst.all_black_line_count)
            print("check_all_black_line_flag : ",self.ctrl.rbst.check_all_black_line_flag)
            print("left_or_right : ", self.ctrl.rbst.left_or_right)
            print("linetrace_next: ", self.ctrl.rbst.linetrace_next)
            print("up_or_down : ", self.ctrl.rbst.up_or_down)
            print("execute_count : ", self.ctrl.rbst.execute_count)
            print("freeball_goal_position_flag: ", self.ctrl.rbst.freeball_goal_position_flag)
            # print("search_road_num : ", self.ctrl.rbst.search_road_num)
            print("len(his) : ", len(self.ctrl.rbst.his))
            print("**************************************************")
            
        
            # データを送信
            if self.ctrl.next_state != State.LINETRACE:
                self.ser.write(self.serial_byte)
            self.ser.flush()
            

if __name__ == "__main__":
    com = Communication()

    # テスト
    #com.test()

    # 通信
    com.communicate()
