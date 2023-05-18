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

class CommunicationService {
    public:
        void send(int* line);
        char receive(); // 受け取った1byteのデータを返す
        // int getMotorDataFromByte(Motor motor, char serial_data);
};

#endif // _COMMUNICATION_REPOSITORY_