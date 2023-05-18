#include "motor_service.hpp"

MotorService::MotorService(SteppingMotor stepping_motor) {
    this->stepping_motor = stepping_motor;
}

// 1byteのデータから必要なバイトを取り出す
int MotorService::getMotorDataFromByte(Motor motor, char serial_data) {
  switch (motor)
  {
  case Motor::STEPPING: // 後ろの3bitを取得する, ステッピングモータ
    return serial_data & 0b00000111;
  case Motor::SERVO: // 後ろから4bit目を取得する, サーボモータ
    return serial_data & 0b00001000;
  case Motor::DC: // 後ろから5bit目を取得する, DCモータ
    return serial_data & 0b00010000;
  }
}

void MotorService::driveMotor(char serial_data) {
    // ステッピングモータ
    this->stepping_motor.moveSteppingMotor(MotorService::getMotorDataFromByte(Motor::STEPPING, serial_data), 20);
    // サーボモータ
    
    // DCモータ
}