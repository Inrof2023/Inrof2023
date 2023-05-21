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
        SteppingMotor stepping_motor;
        ServoMotor servo_motor;
        // DCMotor dc_motor;
        int getMotorDataFromByte(Motor motor, char serial_data);

    public:
        MotorService();
        void setup();
        void driveMotor(char serial_data);
};

#endif // __MOTOR_SERVICE__