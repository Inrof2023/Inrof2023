#include "dc_motor.hpp"

DcMotor::DcMotor() {
    // サーボモータのピンを取得
    this->PIN = DC_PIN;
}

void DcMotor::setup() {
    // DCモータのピンを出力に設定
    pinMode(this->PIN, OUTPUT);
}

void DcMotor::moveDcMotor(char serial_data) {
    if (serial_data) { // DCモータを動かす
        digitalWrite(this->PIN, HIGH);
    } else { // DCモータを止める（動かさない）
        digitalWrite(this->PIN, LOW);
    }
}