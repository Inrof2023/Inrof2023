#include "motor_service.hpp"

// グローバル変数の宣言
// 他の変数名と被らないように
// ###################################################################################################
// ライントレースの方向を格納
enum class DirectionForLineTrace {
  Forward,
  Backward,
};

DirectionForLineTrace direction_for_line_trace = DirectionForLineTrace::Forward; // ライントレースの方向
int SPEED_LEFT_FOR_LINE_TRACE = 100; // 左のステッピングモータの速度（1秒間の回転数）, 200が最大, 0が最小（停止）
int SPEED_RIGHT_FOR_LINE_TRACE = 100; // 右のステッピングモータの速度（一秒間の回転数）, 200が最大, 0が最小（停止）
int COUNT_STEPS_FOR_LINE_TRACE = 0; // ステッピングモータのステップ数をカウントする, 200が最大, 0が最小

float PID_FOR_LINE_TRACE_PRESEN = 0; // 前回の偏差
float PID_FOR_LINE_TRACE_INTEGRAL = 0; // 偏差の積分値

// 割り込みで設定する関数
// グローバル変数を使いまくる
void interrupt(){
  if (COUNT_STEPS_FOR_LINE_TRACE % 100 == 0) {
    float sensor_val = (analogRead(LEFT) + analogRead(SENTER_L) - analogRead(SENTER_R) - analogRead(RIGHT)) / 2 / 1024.0;
    float pid_val = PID_FOR_LINE_TRACE_P * sensor_val + PID_FOR_LINE_TRACE_I * PID_FOR_LINE_TRACE_INTEGRAL + PID_FOR_LINE_TRACE_D * (sensor_val - PID_FOR_LINE_TRACE_PRESEN);
    if (pid_val > 100) pid_val = 100; // 最大値を超えないように
    PID_FOR_LINE_TRACE_PRESEN = sensor_val;
    PID_FOR_LINE_TRACE_INTEGRAL += sensor_val;
    SPEED_LEFT_FOR_LINE_TRACE = 100 - pid_val;
    SPEED_RIGHT_FOR_LINE_TRACE = 100 + pid_val;
  }

  // ライントレースする方向を指定
  switch (direction_for_line_trace)
  {
  case DirectionForLineTrace::Forward:
    digitalWrite(DIR_LEFT, LOW);
    digitalWrite(DIR_RIGHT, HIGH);
    break;
  case DirectionForLineTrace::Backward:
    digitalWrite(DIR_LEFT, HIGH);
    digitalWrite(DIR_RIGHT, LOW);
  }

  // 左のモータを動かす
  // 200 / SPEED_LEFT_FOR_LINE_TRACE がパルスを出す周期
  // これがCOUNT_STEPS_FOR_LINE_TRACEの値を割り切れる時回転する
  // ここは改善の余地がある（パルス幅をもう少し小さくするとか？）
  if(SPEED_LEFT_FOR_LINE_TRACE > 0 && COUNT_STEPS_FOR_LINE_TRACE % (200 / SPEED_LEFT_FOR_LINE_TRACE) == 0){
    digitalWrite(STEP_LEFT,HIGH);
    digitalWrite(STEP_LEFT,LOW);
  }
  if(SPEED_LEFT_FOR_LINE_TRACE > 0 && COUNT_STEPS_FOR_LINE_TRACE % (200 / SPEED_RIGHT_FOR_LINE_TRACE) == 0){
    digitalWrite(STEP_RIGHT,HIGH);
    digitalWrite(STEP_RIGHT,LOW);
  }

  COUNT_STEPS_FOR_LINE_TRACE = (COUNT_STEPS_FOR_LINE_TRACE + 1) % 200;
}

// ###################################################################################################

MotorService::MotorService() {
    SteppingMotor stepping_motor;
    ServoMotor servo_motor;
    this->stepping_motor = stepping_motor;
    this->servo_motor = servo_motor;
    this->motion_state = MotionState::LINETRACE;
}

void MotorService::setup() {
    // セットアップ
    // モータのピンのセットアップとか
    this->stepping_motor.setup();
    this->servo_motor.setup();
}

// // 1byteのデータから必要なバイトを取り出す
// int MotorService::getMotorDataFromByte(Motor motor, char serial_data) {
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
    // ロボットの制御方法（ライントレースまたはカメラ）を決定する
    if (MotorService::getDataFromByte(BitData::LINETRACE, serial_data)) {
      // ライントレース

      // ライントレースする時の方向（前進、後退）を決定する
      // 割り込みする関数にも使うのでグローバル変数に代入する
      if (!MotorService::getDataFromByte(BitData::Direction, serial_data)) { // 0の時は前進
        direction_for_line_trace = DirectionForLineTrace::Forward;
      }
      else { // 1の時は後退
        direction_for_line_trace = DirectionForLineTrace::Backward;
      }

      // StateがLINETRACEではない時（カメラからライントレースに切り替わる時）は割り込みを再開させる
      // StateがLINETRACEの時は何もしない
      if (this->motion_state != MotionState::LINETRACE) {
        // 割り込みを再開させる
        MsTimer2::start();
      }

      // StateをLINETRACEに変更
      this->motion_state = MotionState::LINETRACE;
    }
    else {
      // カメラ

      // StateがLINETRACEの時は割り込みを停止させる
      if (this->motion_state == MotionState::LINETRACE) {
        MsTimer2::stop();
      }

      // StateをCAMERAに変更
      this->motion_state = MotionState::CAMERA;

      // ラズパイから送られてきたデータを元にロボットを動かす
      this->stepping_motor.moveSteppingMotor(MotorService::getDataFromByte(BitData::STEPPING, serial_data), 1);
    }
    // ステッピングモータ
    // this->stepping_motor.moveSteppingMotor(MotorService::getDataFromByte(BitData::STEPPING, serial_data), 1);
    // サーボモータ
    this->servo_motor.moveServoMotor(MotorService::getDataFromByte(BitData::SERVO, serial_data));
    // DCモータ
    // this->dc_motor.moveDCMotor(MotorService::getMotorDataFromByte(Motor::DC, serial_data));
}