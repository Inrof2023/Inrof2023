#include "constants.hpp"
#include "communication_service.hpp"
#include <Arduino.h>

// フォトリフレクタの値を取得してline_arrayに格納
void CommunicationService::readPhotoReflectorValue() {
  this->line_array[0] = analogRead(LEFT);
  this->line_array[1] = analogRead(SENTER_L);
  this->line_array[2] = analogRead(SENTER_R);
  this->line_array[3] = analogRead(RIGHT);
}

// ラズパイから受信
void CommunicationService::send() {

  // フォトリフレクタの値を取得
  // 内部のline_arrayに格納される
  CommunicationService::readPhotoReflectorValue();

  for (int i = 0; i < LINE_ELEMENTS; i++ ){
    Serial.print(this->line_array[i]);
    if (i == LINE_ELEMENTS - 1) Serial.print("\n");
    else Serial.print(",");
  }
}

// ラズパイへ送信
char CommunicationService::receive() {
  if(Serial.available() > 0){ 
      char data[BUFFER_SIZE];
      Serial.readBytes(data, BUFFER_SIZE);

      // デバッグ用
      // int received_data = data[0]; // ここがだいぶ怪しい
      return data[0];
      // Serial.println(data[0]);
      // ここでそれぞれのモータに対して信号を送る
      // この時にdataをbit演算して必要なところだけ取り出す
   }
}
