#ifndef __MOTOR_SERVICE__
#define __MOTOR_SERVICE__

#include <Arduino.h>
#include "constants.hpp"
#include "stepping_motor.hpp"
#include "servo_motor.hpp"
// #include "dc_motor.hpp"

class MotorService {
    private:
        enum class Motor {
            STEPPING,
            SERVO,
            DC
        };
        enum class State {
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
        // DCMotor dc_motor;
        int getMotorDataFromByte(Motor motor, char serial_data);
        int getDataFromByte(BitData bit_data, char serial_data);

    public:
        MotorService();
        void setup();
        void driveMotor(char serial_data);
};

#endif // __MOTOR_SERVICE__