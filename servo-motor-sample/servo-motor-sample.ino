#include <Servo.h> 
Servo servo;
 
const int IN = 2;

void setup() {
 
  servo.attach(IN);   // デジタルピンD3にサーボのSignal(オレンジ)を繋ぐ
 
}
 
void loop() {
  
  servo.write(0);    // サーボを0°の位置に動かす
  delay(1000);
 
  servo.write(90);   // サーボを90°の位置に動かす
  delay(1000);
 
  servo.write(180);  // サーボを180°の位置に動かす
  delay(1000);
 
}