const int DIR_L  = 4;
const int STEP_L = 5;
const int DIR_R = 6;
const int STEP_R = 7;

void setup() {
  // set up left stepping motor
  pinMode(DIR_L, OUTPUT);
  pinMode(STEP_L, OUTPUT);
  digitalWrite(DIR_L, LOW);
  digitalWrite(STEP_L, LOW);

  // set up right stepping motor
  pinMode(DIR_R, OUTPUT);
  pinMode(STEP_R, OUTPUT);
  digitalWrite(DIR_R, LOW);
  digitalWrite(STEP_R, LOW);
}

void loop() {
  
  digitalWrite(DIR_L, HIGH);
  digitalWrite(DIR_R, HIGH);

  for (int i=0; i<200; i++) {
    // rotate light stepping motor
    digitalWrite(STEP_L, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP_L, LOW);
    delayMicroseconds(2000);

    // rotate right stepping motor
    digitalWrite(STEP_R, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP_R, LOW);
    delayMicroseconds(2000);
  }

  delay(1000);

  digitalWrite(DIR_L, LOW);
  digitalWrite(DIR_R, LOW);
  
  for (int i=0; i<200; i++) {
    // rotate light stepping motor
    digitalWrite(STEP_L, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP_L, LOW);
    delayMicroseconds(2000);

    // rotate right stepping motor
    digitalWrite(STEP_R, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP_R, LOW);
    delayMicroseconds(2000);
  }

  delay(1000);

}