#ifndef __DC_MOTOR__
#define __DC_MOTOR__

#include "constants.hpp"
#include <Arduino.h>

<<<<<<< HEAD
class DcMotor {
=======
class DCMotor {
>>>>>>> ab78753 (can communicate but this code must be refactoring)
    private:
        int PIN;
    public:
        DcMotor();
        void setup();
        void moveDcMotor(char serial_data);
};

#endif // __DC_MOTOR__