#ifndef __MOTOR_SERVICE__
#define __MOTOR_SERVICE__

#include <Arduino.h>
#include <MsTimer2.h>
#include "constants.hpp"
#include "stepping_motor.hpp"
#include "servo_motor.hpp"
#include "dc_motor.hpp"

// フォトリフレクタのピン番号
#define LEFT A0
#define SENTER_L A1
#define SENTER_R A2
#define RIGHT A3

#define PID_FOR_LINE_TRACE_P 50
#define PID_FOR_LINE_TRACE_I 0
#define PID_FOR_LINE_TRACE_D 1

class MotorService {
    private:
        // enum class Motor {
        //     STEPPING,
        //     SERVO,
        //     DC
        // };
        enum class MotionState {
            LINETRACE,
            CAMERA,
        };
        enum class BitData {
            STEPPING, // 4bit
            SERVO, // 1bit
            DC, // 1bit
            LINETRACE, // 1bit
            Direction, // 1bit
        };
        SteppingMotor stepping_motor;
        ServoMotor servo_motor;
        DcMotor dc_motor;
        MotionState motion_state;
        // DCMotor dc_motor;
        // int getMotorDataFromByte(Motor motor, char serial_data);
        int getDataFromByte(BitData bit_data, char serial_data);

    public:
        MotorService();
        void setup();
        void driveMotor(char serial_data);
};

// 割り込み用の関数のプロトタイプ宣言
void interrupt();

#endif // __MOTOR_SERVICE__