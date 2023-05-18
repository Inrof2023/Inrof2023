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


class CommunicationRepository {
    public:
        void send(int* line);
        void receive();
};

#endif // _COMMUNICATION_REPOSITORY_