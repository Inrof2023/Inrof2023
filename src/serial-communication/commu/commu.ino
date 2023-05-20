#include <Servo.h>
// #include "constants.hpp"
// #include "stepping_motor.hpp"
#include "motor_service.hpp"
#include "communication_service.hpp"
#include "motor_service.hpp"
Servo servo;

using namespace std;

//100以上を白とみなす
// const int THRESHOLD = 100;
// int line_array[4];

// //サーボモーター
// const int SV = 2;

// //DCモーター
// const int DC_F = 3;

SteppingMotor stepping_motor;

// 通信用のクラス
CommunicationService communication;

MotorService motor_service(stepping_motor);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // servo.attach(SV);
  servo.write(0);
  stepping_motor.setup();
  // pinMode(DC_F, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:

  communication.send();
  char serial_data = communication.receive();
  motor_service.driveMotor(serial_data);
}

// //DC motorによる吸い込み
// void Inhale(bool b) {
//   digitalWrite(DC_F, b);
// }

// //Servo motorによるアーム制御
// void Arm(bool b) {
//   digitalWrite(DC_F, b);
// }
