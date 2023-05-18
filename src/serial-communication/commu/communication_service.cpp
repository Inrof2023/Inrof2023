#include "constants.hpp"
#include "communication_service.hpp"
#include <Arduino.h>

// ラズパイから受信
void CommunicationService::send(int* line_array) {
  int i = 0;
  for (i = 0; i < LINE_ELEMENTS - 1; i++) {
    Serial.print(line_array[i]);
    Serial.print(",");
  }
  Serial.println(line_array[i]);
}

// ラズパイへ送信
int CommunicationService::receive() {
  if(Serial.available() > 0){ 
      char data[BUFFER_SIZE];
      Serial.readBytes(data, BUFFER_SIZE*2);

      // デバッグ用
      // int received_data = data[0]; // ここがだいぶ怪しい
      return data[0];
      // Serial.println(data[0]);
      // ここでそれぞれのモータに対して信号を送る
      // この時にdataをbit演算して必要なところだけ取り出す
   }
}

// // 1byteのデータから必要なバイトを取り出す
// int CommunicationService::getMotorDataFromByte(Motor motor, char serial_data) {
//   switch (motor)
//   {
//   case Motor::STEPPING: // 後ろの3bitを取得する, ステッピングモータ
//     return serial_data & 0b00000111;
//   case Motor::SERVO: // 後ろから4bit目を取得する, サーボモータ
//     return serial_data & 0b00001000;
//   case Motor::DC: // 後ろから5bit目を取得する, DCモータ
//     return serial_data & 0b00010000;
//   }
// }

