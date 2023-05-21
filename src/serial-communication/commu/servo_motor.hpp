#ifndef __SERVO_MOTOR__
#define __SERVO_MOTOR__

#include "constants.hpp"
#include <Arduino.h>
#include <Servo.h>

class ServoMotor {
    private:
        int PIN;
        Servo servo;
    public:
        ServoMotor();
        void setup();
        void moveServoMotor(char serial_data);
};

#endif // __SERVO_MOTOR__