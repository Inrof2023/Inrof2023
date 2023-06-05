// #include<A4988.h>
const int DIR_L  = 4;
const int STEP_L = 5;
const int DIR_R = 6;
const int STEP_R = 7;

enum class Direction {
  Leftward,
  Rightward,
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

//   rotateMotorByStepsInDirection(Direction::Leftward, 230);
}

// 指定された向き（前進または後退）ステップ数だけ回す
void rotateMotorByStepsInDirection(Direction dir, int steps) {

  // モータが回転する方向を設定している
  switch (dir) {
    case Direction::Leftward:
      digitalWrite(DIR_L, HIGH);
      for (int i = 0; i < steps; i++ ){
        digitalWrite(STEP_L, HIGH);
        digitalWrite(STEP_L, LOW);
        delay(20);
      }
      break;
    case Direction::Rightward:
      digitalWrite(DIR_R, HIGH);
      for (int i = 0; i < steps; i++ ) {
        digitalWrite(STEP_R, HIGH);
        digitalWrite(STEP_R, LOW);
        delayMicroseconds(20000);
      }
      break;
  }
}

void loop() {
  rotateMotorByStepsInDirection(Direction::Leftward, 200);
}