#include <Servo.h>
Servo servo;

//フォトリフレクタ
const int LINE_ELEMENTS = 4;

const int LEFT = A0;
const int SENTER_L = A1;
const int SENTER_R = A2;
const int RIGHT = A3;
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

enum class Direction {
  Forward,
  Backward,
  Leftward,
  Rightward
};

// 指定された向き（前進または後退）ステップ数だけ回す
void rotateMotorByStepsInDirection(Direction dir, int steps) {

  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::Forward:
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
    case Direction::Backward:
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
    case Direction::Leftward:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
      // モータをステップ数steps回だけ回転させる（200ステップで一周）
      for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_L, HIGH);
        delayMicroseconds(20000);
        digitalWrite(STEP_L, LOW);
        delayMicroseconds(20000);
      }
    case Direction::Rightward:
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
}

// 前進するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorForwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::Forward, steps);
}

// 後退するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorBackwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::Backward, steps);
}

// 左旋回するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorLeftwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::Leftward, steps);
}

// 右旋回するようにモータをステップ数だけ回す
// rotateMotorByStepsInDirectionのラッパー
void rotateMotorRightwardBySteps(int steps) {
  rotateMotorByStepsInDirection(Direction::Rightward, steps);
}

//受信データ格納
const int BUFFER_SIZE = 10;
byte data[BUFFER_SIZE];

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
  line_array[0] = analogRead(LEFT);
  line_array[1] = analogRead(SENTER_L);
  line_array[2] = analogRead(SENTER_R);
  line_array[3] = analogRead(RIGHT);
  int i = 0;
  for (i = 0; i < LINE_ELEMENTS - 1; i++) {
    Serial.print(line_array[i]);
    Serial.print(",");
  }
  Serial.println(line_array[i]);

  while (Serial.available() <= 0) {
  }
  Serial.readBytes(data, BUFFER_SIZE);
  Serial.print(data[0]);
  Serial.print(data[1]);
  Serial.print(data[2]);
  Serial.print(data[3]);
  Drive(data[0], data[1]);
  Inhale(data[2]);
  Arm(data[3]);
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

//DC motorによる吸い込み
void Inhale(bool b) {
  digitalWrite(DC_F, b);
}

//Servo motorによるアーム制御
void Arm(bool b) {
  digitalWrite(DC_F, b);
}
