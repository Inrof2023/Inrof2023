#ifndef _CONSTANTS_FOR_ARDUINO_
#define _CONSTANTS_FOR_ARDUINO_

#include <Arduino.h>

#define LINE_ELEMENTS 4 // フォトリフレクタの数
#define LEFT A0 // フォトリフレクタ左
#define SENTER_L A1 // フォトリフレクタ真ん中左
#define SENTER_R A2 // フォトリフレクタ真ん中右
#define RIGHT A3 // フォトリフテクタ右

#define DC_PIN 3 // DCモーターのピン番号

<<<<<<< HEAD
#define SERVO_PIN 2 // サーボモーターのピン番号
#define UP_ANGLE 90 // サーボモーターの上向きの角度
#define DOWN_ANGLE 175 // サーボモーターの下向きの角度
=======
#define SERVO_PIN 9 // サーボモーターのピン番号
#define UP_ANGLE 90 // サーボモーターの上向きの角度
#define DOWN_ANGLE 0 // サーボモーターの下向きの角度
>>>>>>> ab78753 (can communicate but this code must be refactoring)

//ステッピングモーター左
#define DIR_LEFT 4
#define STEP_LEFT 5
//ステッピングモーター右
#define DIR_RIGHT 6
#define STEP_RIGHT 7
<<<<<<< HEAD

// using namespace std;
=======
>>>>>>> ab78753 (can communicate but this code must be refactoring)

//100以上を白とみなす
// const int THRESHOLD = 100;

<<<<<<< HEAD
=======
// //サーボモーター
// const int SV = 2;

// //DCモーター
// const int DC_F = 3;

// //ステッピングモーター左
// const int DIR_L = 4;
// const int STEP_L = 5;
// //ステッピングモーター右
// const int DIR_R = 6;
// const int STEP_R = 7;

// //受信データ格納
// const int BUFFER_SIZE = 1;
// byte data[BUFFER_SIZE];

>>>>>>> ab78753 (can communicate but this code must be refactoring)
#endif // _CONSTANTS_FOR_ARDUINO_