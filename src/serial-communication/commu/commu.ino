#include <Servo.h>
// #include "constants.hpp"
// #include "stepping_motor.hpp"
#include "motor_service.hpp"
#include "communication_service.hpp"
#include "motor_service.hpp"
Servo servo;

using namespace std;

//フォトリフレクタ
// const int LINE_ELEMENTS = 4;

// const int LEFT = A0;
// const int SENTER_L = A1;
// const int SENTER_R = A2;
// const int RIGHT = A3;

//100以上を白とみなす
const int THRESHOLD = 100;
int line_array[4];

//サーボモーター
const int SV = 2;

//DCモーター
const int DC_F = 3;

//ステッピングモーター左
const int DIR_L = 4;
const int STEP_L = 5;
//ステッピングモーター右
const int DIR_R = 6;
const int STEP_R = 7;

SteppingMotor stepping_motor;

// 通信用のクラス
CommunicationService communication;

MotorService motor_service(stepping_motor);

//受信データ格納
// const int BUFFER_SIZE = 1;
char data[BUFFER_SIZE];

// enum class Direction {
//   FORWARD,
//   BACKWARD,
//   LEFTWORD,
//   RIGHTWORD
// };

// enum class Motor {
//   STEPPING,
//   SERVO,
//   DC
// };

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  servo.attach(SV);
  servo.write(0);
  pinMode(DC_F, OUTPUT);
  pinMode(DIR_L, OUTPUT);
  pinMode(STEP_L, OUTPUT);
  digitalWrite(DIR_L, LOW);
  digitalWrite(STEP_L, LOW);
  pinMode(DIR_R, OUTPUT);
  pinMode(STEP_R, OUTPUT);
  digitalWrite(DIR_R, LOW);
  digitalWrite(STEP_R, LOW);

}

void loop() {
  // put your main code here, to run repeatedly:

  communication.send();
  char serial_data = communication.receive();
  motor_service.driveMotor(serial_data);
}

//DC motorによる吸い込み
void Inhale(bool b) {
  digitalWrite(DC_F, b);
}

//Servo motorによるアーム制御
void Arm(bool b) {
  digitalWrite(DC_F, b);
}
