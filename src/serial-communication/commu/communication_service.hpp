#ifndef _COMMUNICATION_REPOSITORY_
#define _COMMUNICATION_REPOSITORY_

// フォトリフレクタの数
#define LINE_ELEMENTS 4

// フォトリフレクタのピン番号
#define LEFT A0
#define SENTER_L A1
#define SENTER_R A2
#define RIGHT A3

// バッファサイズ
#define BUFFER_SIZE 1

#include "data_receive_result_object.hpp"

class CommunicationService {
    private:
        int line_array[LINE_ELEMENTS];
        void readPhotoReflectorValue();
    public:
<<<<<<< HEAD
        void send(int* line);
        char receive(); // 受け取った1byteのデータを返す
        // int getMotorDataFromByte(Motor motor, char serial_data);
=======
        void send(); // フォトリフレクタのデータをラズパイへ送る
<<<<<<< HEAD
        char receive(); // 受け取った1byteのデータを返す
>>>>>>> 11b9886 (split some class. conducted the actual machine test.)
=======
        DataReceiveResultObject receive(); // 受け取った1byteのデータを返す
>>>>>>> 2ce2c72 (add data_receive_result_object class. conducted the actual machine test.)
};

#endif // _COMMUNICATION_REPOSITORY_