#ifndef __MOTOR_CONTROLLER_SERVICE__
#define __MOTOR_CONTROLLER_SERVICE__

#include <Arduino.h>
#include "motor_service.hpp"
#include "data_receive_result_object.hpp"
#include "communication_service.hpp"

class MotorControllerApplication {
    private:
        CommunicationService communication_service;
        MotorService motor_service;

    public:
        MotorControllerApplication();
        void setup();
        void runMotorControlFlow();    
};

#endif // __MOTOR_CONTROLLER_SERVICE__