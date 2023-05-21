#include "servo_motor.hpp"

ServoMotor::ServoMotor() {
    // サーボモータを宣言して初期化
    // クラスのservoに格納する
    Servo servo;
    this -> servo = servo;
    this->PIN = SERVO_PIN;
}

void ServoMotor::setup() {
    // サーボモータのピンを出力に設定
    pinMode(SERVO_PIN, OUTPUT);
    this->servo.attach(this->PIN);
    this->servo.write(0); // 初期位置に戻す
}

void ServoMotor::moveServoMotor(char serial_data) {
    if (serial_data) {
        this->servo.write(UP_ANGLE);
        delay(1000);
        this->servo.write(DOWN_ANGLE);
        delay(1000);
    } else {
        this->servo.write(DOWN_ANGLE);
    }
}