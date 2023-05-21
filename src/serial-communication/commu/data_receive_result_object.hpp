#ifndef __DATA_RECEIVE_RESULT_OBJECT__
#define __DATA_RECEIVE_RESULT_OBJECT__

#include <Arduino.h>

using namespace std;

class DataReceiveResultObject {
    private:
        bool is_success;
        char serial_data;

    public:
        DataReceiveResultObject(bool is_success, char serial_data);
        bool getIsSuccess();
        char getSerialData();
};


#endif // __DATA_RECEIVE_RESULT_OBJECT__