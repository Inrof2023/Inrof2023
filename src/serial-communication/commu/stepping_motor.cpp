#include <Arduino.h>
#include "stepping_motor.hpp"

SteppingMotor::SteppingMotor() {
  // pinModeの設定
  // 左のモータ
  pinMode(DIR_L, OUTPUT);
  pinMode(STEP_L, OUTPUT);
  digitalWrite(DIR_L, LOW);
  digitalWrite(STEP_L, LOW);
  // 右のモータ
  pinMode(DIR_R, OUTPUT);
  pinMode(STEP_R, OUTPUT);
  digitalWrite(DIR_R, LOW);
  digitalWrite(STEP_R, LOW);
  
  // メンバ変数の設定
  this->DIR_L = DIR_LEFT;
  this->STEP_L = STEP_LEFT;
  this->DIR_R = DIR_RIGHT;
  this->STEP_R = STEP_RIGHT;
}

void SteppingMotor::rotateMotorByStepsInDirection(Direction dir, int steps) {
  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::FORWARD:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_L, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_L, LOW);
        delayMicroseconds(20000);

        digitalWrite(STEP_R, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_R, LOW);
        delayMicroseconds(20000);
      }
    case Direction::BACKWARD:
      digitalWrite(DIR_L, HIGH);
      digitalWrite(DIR_R, LOW);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_L, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_L, LOW);
        delayMicroseconds(20000);

        digitalWrite(STEP_R, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_R, LOW);
        delayMicroseconds(20000);
      }
    case Direction::LEFTWORD:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_L, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_L, LOW);
        delayMicroseconds(20000);
      }
    case Direction::RIGHTWORD:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_R, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_R, LOW);
        delayMicroseconds(20000);
      }
  }
}

void SteppingMotor::rotateMotorForwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::FORWARD, steps);
}

void SteppingMotor::rotateMotorBackwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::BACKWARD, steps);
}

void SteppingMotor::rotateMotorLeftwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::LEFTWORD, steps);
}

void SteppingMotor::rotateMotorRightwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::RIGHTWORD, steps);
}

void SteppingMotor::moveSteppingMotor(int sirial_data, int steps) {
  switch (sirial_data)
  {
  case 0b000: // 停止
    break;
  case 0b001: // 前進
    SteppingMotor::rotateMotorForwardBySteps(steps);
    break;
  case 0b010: // 後退
    SteppingMotor::rotateMotorBackwardBySteps(steps);
    break;
  case 0b011: // 左回り
    SteppingMotor::rotateMotorLeftwardBySteps(steps);
    break;
  case 0b100: // 右回り
    SteppingMotor::rotateMotorRightwardBySteps(steps);
    break;
  }
}