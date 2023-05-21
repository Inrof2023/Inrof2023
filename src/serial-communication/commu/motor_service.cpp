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

void MotorService::driveMotor(char serial_data) {
    // ステッピングモータ
    this->stepping_motor.moveSteppingMotor(MotorService::getMotorDataFromByte(Motor::STEPPING, serial_data), 20);
    // サーボモータ
    this->servo_motor.moveServoMotor(MotorService::getMotorDataFromByte(Motor::SERVO, serial_data));
    // DCモータ
    // this->dc_motor.moveDCMotor(MotorService::getMotorDataFromByte(Motor::DC, serial_data));
}