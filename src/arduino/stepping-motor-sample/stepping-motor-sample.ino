// #include<A4988.h>
const int DIR_L  = 4;
const int STEP_L = 5;
const int DIR_R = 6;
const int STEP_R = 7;

enum class Direction {
  Forward, 
  Backward
};

void setupMotorPin(int DIR, int STEP) {
  pinMode(DIR, OUTPUT);
  pinMode(STEP, OUTPUT);
  digitalWrite(DIR, LOW);
  digitalWrite(STEP, LOW);
}

void setup() {
  // setup left motor pin
  setupMotorPin(DIR_L, STEP_L);

  // setup right motor pin
  setupMotorPin(DIR_R, STEP_R);
}

// 指定された向き（前進または後退）ステップ数だけ回す
void rotateMotorByStepsInDirection(Direction dir, int steps) {

  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::Forward:
      digitalWrite(DIR_L, LOW);
      digitalWrite(DIR_R, HIGH);
    case Direction::Backward:
      digitalWrite(DIR_L, HIGH);
      digitalWrite(DIR_R, LOW);
  }

  // モータをステップ数steps回だけ回転させる（200ステップで一周）
  for (int i = 0; i < steps; i++ ){
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


void loop() {
  rotateMotorForwardBySteps(100);
}