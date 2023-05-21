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
        void send(); // フォトリフレクタのデータをラズパイへ送る
        DataReceiveResultObject receive(); // 受け取った1byteのデータを返す
};

#endif // _COMMUNICATION_REPOSITORY_