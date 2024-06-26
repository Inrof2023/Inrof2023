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
int SPEED_LEFT_FOR_LINE_TRACE = 33; // 左のステッピングモータの速度（1秒間の回転数）, 200が最大, 0が最小（停止）
int SPEED_RIGHT_FOR_LINE_TRACE = 33; // 右のステッピングモータの速度（一秒間の回転数）, 200が最大, 0が最小（停止）
int COUNT_STEPS_FOR_LINE_TRACE = 0; // ステッピングモータのステップ数をカウントする, 200が最大, 0が最小

float PID_FOR_LINE_TRACE_PRESEN = 0; // 前回の偏差
float PID_FOR_LINE_TRACE_INTEGRAL = 0; // 偏差の積分値

float ACCELERATION_CONTROL = 0.0; // 加速度制御, 線形加速度

// 割り込みで設定する関数
// グローバル変数を使いまくる
// PID制御
void interrupt(){
  if (COUNT_STEPS_FOR_LINE_TRACE % 10 == 0) {
    float sensor_val = (analogRead(LEFT)*1.2 + analogRead(SENTER_L) - analogRead(SENTER_R) - analogRead(RIGHT)*1.2) / 2 / 1024.0;
    float pid_val = PID_FOR_LINE_TRACE_P * sensor_val + PID_FOR_LINE_TRACE_I * PID_FOR_LINE_TRACE_INTEGRAL + PID_FOR_LINE_TRACE_D * (sensor_val - PID_FOR_LINE_TRACE_PRESEN);
    if (pid_val > 33) pid_val = 33; // 最大値を超えないように
    if (-33 > pid_val) pid_val = -33;
    PID_FOR_LINE_TRACE_PRESEN = sensor_val;
    PID_FOR_LINE_TRACE_INTEGRAL += sensor_val;
    // SPEED_LEFT_FOR_LINE_TRACE = (int)((50 + pid_val) * ACCELERATION_CONTROL);
    // SPEED_RIGHT_FOR_LINE_TRACE = (int)((50 - pid_val) * ACCELERATION_CONTROL);
    SPEED_LEFT_FOR_LINE_TRACE = 33 + pid_val;
    SPEED_RIGHT_FOR_LINE_TRACE = 33 - pid_val;
    // Serial.print(SPEED_LEFT_FOR_LINE_TRACE);
    // Serial.print(":");
    // Serial.print(SPEED_RIGHT_FOR_LINE_TRACE);
    // Serial.print(":");
    // SPEED_LEFT_FOR_LINE_TRACE = 50 - pid_val;
    // SPEED_RIGHT_FOR_LINE_TRACE = 50 + pid_val;
  }

  if (SPEED_LEFT_FOR_LINE_TRACE == 0) SPEED_LEFT_FOR_LINE_TRACE = 1;
  if (SPEED_RIGHT_FOR_LINE_TRACE == 0) SPEED_RIGHT_FOR_LINE_TRACE = 1;
  
  // // ライントレースする方向を指定
  // switch (direction_for_line_trace)
  // {
  // case DirectionForLineTrace::Forward:
  //   digitalWrite(DIR_LEFT, LOW);
  //   digitalWrite(DIR_RIGHT, HIGH);
  //   break;
  // case DirectionForLineTrace::Backward:
  //   digitalWrite(DIR_LEFT, HIGH);
  //   digitalWrite(DIR_RIGHT, LOW);
  // }

  digitalWrite(DIR_LEFT, LOW);
  digitalWrite(DIR_RIGHT, HIGH);

  // 左のモータを動かす
  // 200 / SPEED_LEFT_FOR_LINE_TRACE がパルスを出す周期
  // これがCOUNT_STEPS_FOR_LINE_TRACEの値を割り切れる時回転する
  // ここは改善の余地がある（パルス幅をもう少し小さくするとか？）
  if(SPEED_LEFT_FOR_LINE_TRACE > 0 && COUNT_STEPS_FOR_LINE_TRACE % (66 / SPEED_LEFT_FOR_LINE_TRACE) == 0){
    digitalWrite(STEP_LEFT,HIGH);
    digitalWrite(STEP_LEFT,LOW);
  }
  if(SPEED_RIGHT_FOR_LINE_TRACE > 0 && COUNT_STEPS_FOR_LINE_TRACE % (66 / SPEED_RIGHT_FOR_LINE_TRACE) == 0){
    digitalWrite(STEP_RIGHT,HIGH);
    digitalWrite(STEP_RIGHT,LOW);
  }

  COUNT_STEPS_FOR_LINE_TRACE = (COUNT_STEPS_FOR_LINE_TRACE + 1) % 66;
}

// ###################################################################################################

MotorService::MotorService() {
    // それぞれのモータのインスタンスを作る
    SteppingMotor stepping_motor;
    ServoMotor servo_motor;
    DcMotor dc_motor;

    // インスタンスをクラスのメンバに格納する
    this->stepping_motor = stepping_motor;
    this->servo_motor = servo_motor;
    this->dc_motor = dc_motor;
    // ここを後で変更する
    this->motion_state = MotionState::CAMERA;
    // this->motion_state = MotionState::LINETRACE;
    // MsTimer2::start(); // 後で消す
}

void MotorService::setup() {
    // セットアップ
    // モータのピンのセットアップとか
    this->stepping_motor.setup();
    this->servo_motor.setup();
    this->dc_motor.setup();
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
      // ここまでOK
      // Serial.print("Hello");

      // ライントレースする時の方向（前進、後退）を決定する
      // 割り込みする関数にも使うのでグローバル変数に代入する
      if (!MotorService::getDataFromByte(BitData::Direction, serial_data)) { // 0の時は前進
        direction_for_line_trace = DirectionForLineTrace::Forward;
        // ここまでOK
      }
      else { // 1の時は後退
        direction_for_line_trace = DirectionForLineTrace::Backward;
      }

      if (ACCELERATION_CONTROL < 1.0) {
        ACCELERATION_CONTROL += 0.05; // ここは後で調節
      }

      // StateがLINETRACEではない時（カメラからライントレースに切り替わる時）は割り込みを再開させる
      // StateがLINETRACEの時は何もしない
      if (this->motion_state != MotionState::LINETRACE) {
        // 割り込みを再開させる
        MsTimer2::start();
      }

      // Serial.print(SPEED_LEFT_FOR_LINE_TRACE);
      // Serial.print(":");
      // Serial.print(SPEED_RIGHT_FOR_LINE_TRACE);
      // Serial.print(":");

      // StateをLINETRACEに変更
      this->motion_state = MotionState::LINETRACE;
    }
    else {
      // カメラ

      // StateがLINETRACEの時は割り込みを停止させる
      if (this->motion_state == MotionState::LINETRACE) {
        MsTimer2::stop(); // 割り込みをストップする
        ACCELERATION_CONTROL = 0.0; // 加速度をリセットする
      }

      // StateをCAMERAに変更
      this->motion_state = MotionState::CAMERA;

      // ラズパイから送られてきたデータを元にロボットを動かす
      this->stepping_motor.moveSteppingMotor(MotorService::getDataFromByte(BitData::STEPPING, serial_data), 1);
      // Serial.print("Hello");
    }
    // ステッピングモータ
    // this->stepping_motor.moveSteppingMotor(MotorService::getDataFromByte(BitData::STEPPING, serial_data), 1);
    // サーボモータ
    this->servo_motor.moveServoMotor(MotorService::getDataFromByte(BitData::SERVO, serial_data));
    // DCモータ
    this->dc_motor.moveDcMotor(MotorService::getDataFromByte(BitData::DC, serial_data));
    // this->dc_motor.moveDCMotor(MotorService::getMotorDataFromByte(Motor::DC, serial_data));
}