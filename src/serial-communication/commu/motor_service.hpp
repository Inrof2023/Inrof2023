#ifndef __MOTOR_SERVICE__
#define __MOTOR_SERVICE__

#include <Arduino.h>
#include "stepping_motor.hpp"

class MotorService {
    private:
        enum class Motor {
            STEPPING,
            SERVO,
            DC
        };
        SteppingMotor stepping_motor;
        int getMotorDataFromByte(Motor motor, char serial_data);

    public:
        MotorService(SteppingMotor stepping_motor);
        void driveMotor(char serial_data);
};

#endif // __MOTOR_SERVICE__