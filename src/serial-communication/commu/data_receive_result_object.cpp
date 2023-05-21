#include "data_receive_result_object.hpp"

DataReceiveResultObject::DataReceiveResultObject(bool is_success, char serial_data) {
    this->is_success = is_success;
    this->serial_data = serial_data;
}

bool DataReceiveResultObject::getIsSuccess() {
    return this->is_success;
}

char DataReceiveResultObject::getSerialData() {
    return this->serial_data;
}