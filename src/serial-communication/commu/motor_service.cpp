#include "motor_service.hpp"

MotorService::MotorService() {
    SteppingMotor stepping_motor;
    ServoMotor servo_motor;
    this->stepping_motor = stepping_motor;
    this->servo_motor = servo_motor;
}

void MotorService::setup() {
    // セットアップ
    // モータのピンのセットアップとか
    this->stepping_motor.setup();
    this->servo_motor.setup();
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

// 1byteのデータから必要なバイトを取り出す
int MotorService::getDataFromByte(BitData bit_data, char serial_data) {
  switch (bit_data)
  {
    case BitData::STEPPING: // 後ろの4bitを取得する, ステッピングモータ
      return serial_data & 0b00001111;
    case BitData::SERVO: // 後ろから5bit目を取得する, サーボモータ
      return serial_data & 0b00010000;
    case BitData::DC: // 後ろから6bit目を取得する, DCモータ
      return serial_data & 0b00100000;
    case BitData::LINETRACE: // 後ろから7bit目を取得する, ライントレース
      return serial_data & 0b01000000;
    case BitData::Direction: // 後ろから8bit目を取得する, ライントレースをするときの方向
      return serial_data & 0b10000000;
  }
}

void MotorService::driveMotor(char serial_data) {
    // ステッピングモータ
    this->stepping_motor.moveSteppingMotor(MotorService::getMotorDataFromByte(Motor::STEPPING, serial_data), 1);
    // サーボモータ
    this->servo_motor.moveServoMotor(MotorService::getMotorDataFromByte(Motor::SERVO, serial_data));
    // DCモータ
    // this->dc_motor.moveDCMotor(MotorService::getMotorDataFromByte(Motor::DC, serial_data));
}