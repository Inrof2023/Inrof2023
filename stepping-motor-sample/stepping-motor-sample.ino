#include <A4988.h>

const int MOTOR_STEPS = 200;
const int DIR_L  = 4;
const int STEP_L = 5;
const int DIR_R = 6;
const int STEP_R = 7;

float rpm = 10;
int microsteps = 30;

A4988 stepper_L(MOTOR_STEPS, DIR_L, STEP_L);
A4988 stepper_R(MOTOR_STEPS, DIR_R, STEP_R);

void setup() {
  stepper_L.begin(rpm, microsteps);
  stepper_R.begin(rpm, microsteps);
}

void loop() {
  
  stepper_L.rotate(360);
  stepper_R.rotate(-360);
  delay(1000);
}