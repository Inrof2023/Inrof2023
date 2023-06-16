#include "motor_controller_application.hpp"

using namespace std;

//100以上を白とみなす
// const int THRESHOLD = 100;

MotorControllerApplication motor_controller_application;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  MsTimer2::set(15, interrupt);
  motor_controller_application.setup();
}

void loop() {
  // put your main code here, to run repeatedly:
  motor_controller_application.runMotorControlFlow();
}