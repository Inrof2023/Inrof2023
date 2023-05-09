const int DIR  = 4;
const int STEP = 5;

void setup() {
  pinMode(DIR, OUTPUT);
  pinMode(STEP, OUTPUT);
  digitalWrite(DIR, LOW);
  digitalWrite(STEP, LOW);
}

void loop() {
  
  digitalWrite(DIR, HIGH);

  for (int i=0; i<200; i++) {
    digitalWrite(STEP, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP, LOW);
    delayMicroseconds(2000);
  }

  delay(1000);

  digitalWrite(DIR, LOW);
  
  for (int i=0; i<200; i++) {
    digitalWrite(STEP, HIGH);
    delayMicroseconds(2000);
    digitalWrite(STEP, LOW);
    delayMicroseconds(2000);
  }

  delay(1000);

}