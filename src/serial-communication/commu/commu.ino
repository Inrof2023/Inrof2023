#include <Servo.h>
// #include "constants.hpp"
// #include "stepping_motor.hpp"
#include "motor_service.hpp"
#include "communication_service.hpp"
#include "motor_service.hpp"
#include "servo_motor.hpp"
#include "data_receive_result_object.hpp"
Servo servo;

using namespace std;

//100以上を白とみなす
// const int THRESHOLD = 100;
// int line_array[4];

// //サーボモーター
// const int SV = 2;

// //DCモーター
// const int DC_F = 3;

// ステッピングモータ
SteppingMotor stepping_motor;

// サーボモータ
ServoMotor servo_motor;

// 通信用のクラス
CommunicationService communication;

MotorService motor_service(stepping_motor, servo_motor);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // stepping_motor.setup();
  motor_service.setup();
  // pinMode(DC_F, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  communication.send();
  // char serial_data = communication.receive();
  DataReceiveResultObject data_receive_result_object = communication.receive();
  if (data_receive_result_object.getIsSuccess()) {
    // データが送られてきている時だけ動作する
    motor_service.driveMotor(data_receive_result_object.getSerialData());
  } else {
    // データが送られてきていないときはストップ
  }
  // motor_service.driveMotor(serial_data);
}

// //DC motorによる吸い込み
// void Inhale(bool b) {
//   digitalWrite(DC_F, b);
// }

// //Servo motorによるアーム制御
// void Arm(bool b) {
//   digitalWrite(DC_F, b);
// }
