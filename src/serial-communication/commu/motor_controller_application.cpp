#include "motor_controller_application.hpp"

MotorControllerApplication::MotorControllerApplication() {
    // 通信用のクラス
    CommunicationService communication_service;

    // MotorService motor_service(stepping_motor, servo_motor);
    MotorService motor_service;

    this->communication_service = communication_service;
    this->motor_service = motor_service;
}

void MotorControllerApplication::setup() {
    // セットアップ
    // モータのピンのセットアップとか
    this->motor_service.setup();
}

void MotorControllerApplication::runMotorControlFlow() {
    // モータの制御フロー
    // 1. シリアル通信でデータを渡す
    this->communication_service.send();

    // 2. シリアル通信でデータを受け取る
    DataReceiveResultObject data_receive_result_object = this->communication_service.receive();

    // 3. 受け取ったデータでモータを動かす
    if (data_receive_result_object.getIsSuccess()) {
        this->motor_service.driveMotor(data_receive_result_object.getSerialData());
    } else {
        // 受け取ったデータがなかったら何もしない
    }

    // // 4. バッファを空にする
    // Serial.flush();
}