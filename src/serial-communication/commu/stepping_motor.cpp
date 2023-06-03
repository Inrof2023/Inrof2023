#include <Arduino.h>
#include "stepping_motor.hpp"

SteppingMotor::SteppingMotor() {
  // メンバ変数の設定
  this->DIR_L = DIR_LEFT;
  this->STEP_L = STEP_LEFT;
  this->DIR_R = DIR_RIGHT;
  this->STEP_R = STEP_RIGHT;
}

void SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide dir) {
  switch (dir)
  {
  case SteppingMotorSide::LEFT:
    digitalWrite(this->STEP_L, HIGH);
    digitalWrite(this->STEP_L, LOW);
    delay(20);
    /* code */
    break;
  case SteppingMotorSide::RIGHT:
    digitalWrite(this->STEP_R, HIGH);
    digitalWrite(this->STEP_R, LOW);
    delay(20);
    break;
  }
}

void SteppingMotor::setup() {
  pinMode(this->DIR_L, OUTPUT);
  pinMode(this->STEP_L, OUTPUT);
  digitalWrite(this->DIR_L, LOW);
  digitalWrite(this->STEP_L, LOW);
  // 右のモータ
  pinMode(this->DIR_R, OUTPUT);
  pinMode(this->STEP_R, OUTPUT);
  digitalWrite(this->DIR_R, LOW);
  digitalWrite(this->STEP_R, LOW);
}

void SteppingMotor::rotateMotorByStepsInDirection(Direction dir, int steps) {
  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::FORWARD:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::LEFT);
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::RIGHT);
      }
      break;
    case Direction::BACKWARD:
      digitalWrite(DIR_L, HIGH);
      digitalWrite(DIR_R, LOW);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::LEFT);
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::RIGHT);
      }
      break;
    case Direction::LEFT_WORD:
      digitalWrite(DIR_L, LOW);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::LEFT);
      }
      break;
    case Direction::RIGHT_WORD:
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::RIGHT);
      break;
    case Direction::LEFT_BACK_WORD:
      digitalWrite(DIR_L, HIGH);
      for (int i = 0; i < steps; i++) {
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::LEFT);
      }
      break;
    case Direction::RIGHT_BACK_WORD:
      digitalWrite(DIR_R, LOW);
      for (int i = 0; i < steps; i++) {
        SteppingMotor::rotateMotorOneStepInDirection(SteppingMotorSide::RIGHT);
      }
      break;
  }
}

// ここら辺ラッパー関数だから気にしない
void SteppingMotor::rotateMotorForwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::FORWARD, steps);
}

void SteppingMotor::rotateMotorBackwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::BACKWARD, steps);
}

void SteppingMotor::rotateMotorLeftwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::LEFT_WORD, steps);
}

void SteppingMotor::rotateMotorRightwardBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::RIGHT_WORD, steps);
}

void SteppingMotor::rotateMotorLeftBackBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::LEFT_BACK_WORD, steps);
}

void SteppingMotor::rotateMotorRightBackBySteps(int steps) {
  SteppingMotor::rotateMotorByStepsInDirection(Direction::RIGHT_BACK_WORD, steps);
}

void SteppingMotor::rotateMotorOneRotation() {
  SteppingMotor::
}

void SteppingMotor::moveSteppingMotor(int sirial_data, int steps) {
  switch (sirial_data)
  {
  case 0b0000: // 停止
    break;
  case 0b0001: // 前進
    SteppingMotor::rotateMotorForwardBySteps(steps);
    break;
  case 0b0010: // 後退
    SteppingMotor::rotateMotorBackwardBySteps(steps);
    break;
  case 0b0011: // 左回り
    SteppingMotor::rotateMotorLeftwardBySteps(steps);
    break;
  case 0b0100: // 右回り
    SteppingMotor::rotateMotorRightwardBySteps(steps);
    break;
  case 0b0101: // 左回り後ろ
    SteppingMotor::rotateMotorLeftBackBySteps(steps);
    break;
  case 0b0110: // 右回り後ろ
    SteppingMotor::rotateMotorRightBackBySteps(steps);
    break;
  case 0b0111: // 左旋回前（半分）
    SteppingMotor::rotateMotorLeftwardBySteps(230);
    break;
  case 0b1000: // 右旋回（半分）
    SteppingMotor::rotateMotorRightwardBySteps(230);
    break;
  case 0b1001: // 左旋回後ろ（半分）
    SteppingMotor::rotateMotorLeftBackBySteps(230);
    break;
  case 0b1010: // 右旋回後ろ（半分）
    SteppingMotor::rotateMotorRightBackBySteps(230);
    break;
  case 0b1011: // 方向転換, ここはテストする
    SteppingMotor::rotateMotorLeftBackBySteps(450);
    // ちょっと前に行くけどタイヤを真っ直ぐにしてからかなー
  }
}