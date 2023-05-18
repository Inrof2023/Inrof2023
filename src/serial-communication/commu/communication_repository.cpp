#include "constants.hpp"
#include "communication_repository.hpp"
#include <Arduino.h>

// ラズパイから受信
void CommunicationRepository::send(int* line_array) {
  int i = 0;
  for (i = 0; i < LINE_ELEMENTS - 1; i++) {
    Serial.print(line_array[i]);
    Serial.print(",");
  }
  Serial.println(line_array[i]);
}

// ラズパイへ送信
void CommunicationRepository::receive() {
  if(Serial.available() > 0){ 
      char data[BUFFER_SIZE*2];
      Serial.readBytes(data, BUFFER_SIZE*2);

      // ここでそれぞれのモータに対して信号を送る
      // この時にdataをbit演算して必要なところだけ取り出す
   }
}