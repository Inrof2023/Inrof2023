#include <Servo.h>
// #include "constants.hpp"
#include "stepping_motor.hpp"
#include "communication_service.hpp"
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

// 通信用のクラス
CommunicationService communication;

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

// これ後でクラスに書き換えるからいらないかなー
enum class SteppingSide{
  LEFT,
  RIGHT
};

// ステッピングモータ関係の関数

// 指定された向き（前進または後退）ステップ数だけ回す
void rotateMotorByStepsInDirection(Direction dir, int steps) {

  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::FORWARD:
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
      break;
    case Direction::BACKWARD:
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
      break;
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
      break;
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
      break;
  }
}

// 前進するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorForwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::FORWARD, steps);
}

// 後退するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorBackwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::BACKWARD, steps);
}

// 左旋回するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorLeftwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::LEFTWORD, steps);
}

// 右旋回するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorRightwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::RIGHTWORD, steps);
}

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

void Drive(bool b0, bool b1) {
  //直進
  if (!b0 & !b1) {
    rotateMotorForwardBySteps(100);
  }
  //後進
  if (!b0 & b1) {
    rotateMotorBackwardBySteps(100);
  }
  //左旋回
  if (b0 & !b1) {
    rotateMotorLeftwardBySteps(100);
  }
  //右旋回
  if (b0 & b1) {
    rotateMotorRightwardBySteps(100);
  }
}

void readPhotoReflectorValue(int* line_array) {
  // int line_array[LINE_ELEMENTS];
  line_array[0] = analogRead(LEFT);
  line_array[1] = analogRead(SENTER_L);
  line_array[2] = analogRead(SENTER_R);
  line_array[3] = analogRead(RIGHT);
  // return line_array;
}

// // ラズパイに信号を送信する
// void sendSignalToRaspberryPi(int* line_array) {
//   int i = 0;
//   for (i = 0; i < LINE_ELEMENTS - 1; i++) {
//     Serial.print(line_array[i]);
//     Serial.print(",");
//   }
//   Serial.println(line_array[i]);
// }

// void receiveSignalFromRaspberryPi() {
//   if(Serial.available() > 0){ 
//       Serial.readBytes(data, BUFFER_SIZE);

//       // ここでそれぞれのモータに対して信号を送る
//       // この時にdataをbit演算して必要なところだけ取り出す
//    }
// }

void loop() {
  // put your main code here, to run repeatedly:

  int line_array[LINE_ELEMENTS];
  readPhotoReflectorValue(line_array);
  communication.send(line_array);
  char data = communication.receive();

  // 後ろの3bitを取得する
  // 0b00000111とAND演算する
  int and_data = data & 0b00000111;
  if (and_data == 0b00000001) {
    rotateMotorForwardBySteps(10);
  }
  // rotateMotorForwardBySteps(10);
  
  // ここビット単位なので注意が必要
  // まずは1byteのデータから当該箇所のビット列を取り出す関数extractBitFromByteが必要
  // Drive(data[0], data[1]);
  // Inhale(data[2]);
  // Arm(data[3]);
}

//DC motorによる吸い込み
void Inhale(bool b) {
  digitalWrite(DC_F, b);
}

//Servo motorによるアーム制御
void Arm(bool b) {
  digitalWrite(DC_F, b);
}
