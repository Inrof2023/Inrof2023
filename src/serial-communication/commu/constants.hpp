#ifndef _CONSTANTS_FOR_ARDUINO_
#define _CONSTANTS_FOR_ARDUINO_

#include <Arduino.h>

#define LINE_ELEMENTS 4 // フォトリフレクタの数
#define LEFT A0 // フォトリフレクタ左
#define SENTER_L A1 // フォトリフレクタ真ん中左
#define SENTER_R A2 // フォトリフレクタ真ん中右
#define RIGHT A3 // フォトリフテクタ右

#define DC_PIN 9 // DCモーターのピン番号

#define SERVO_PIN 2 // サーボモーターのピン番号
#define UP_ANGLE 90 // サーボモーターの上向きの角度
#define DOWN_ANGLE 180 // サーボモーターの下向きの角度

//ステッピングモーター左
#define DIR_LEFT 4
#define STEP_LEFT 5
//ステッピングモーター右
#define DIR_RIGHT 6
#define STEP_RIGHT 7

// using namespace std;

//100以上を白とみなす
// const int THRESHOLD = 100;

#endif // _CONSTANTS_FOR_ARDUINO_