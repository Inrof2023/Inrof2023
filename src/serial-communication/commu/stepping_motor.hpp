#ifndef __STEPPING_MOTOR__ 
#define __STEPPING_MOTOR__

#include "constants.hpp"

// 方向を表す列挙体
enum class Direction {
  FORWARD,
  BACKWARD,
  LEFT_WORD,
  RIGHT_WORD,
  LEFT_BACK_WORD,
  RIGHT_BACK_WORD,
  LEFT_HALF_FORWARD_ROTATION,
  RIGHT_HALF_FORWARD_ROTATION,
  LEFT_HALF_BACK_ROTATION,
  RIGHT_HALF_BACK_ROTATION,
  CHANGE_DIRECTION
};

// ステッピングモータクラス
class SteppingMotor {
  private:

    enum class SteppingMotorSide {
      LEFT,
      RIGHT
    };

    // privateメンバ
    // ステッピングモータ左
    int DIR_L;
    int STEP_L;
    // ステッピングモータ右
    int DIR_R;
    int STEP_R;
    // 左右のモータを表す列挙体
    SteppingMotorSide side;

    void rotateMotorByStepsInDirection(Direction dir, int steps); // 指定された向き（前進または後退）ステップ数だけ回す
    void rotateMotorOneStepInDirection(SteppingMotorSide dir); // 指定された向き（前進または後退）1ステップだけ回す
  public: 
    SteppingMotor(); // コンストラクタ
    void setup();

    void rotateMotorForwardBySteps(int steps); // 前進
    void rotateMotorBackwardBySteps(int steps); // 後退
    void rotateMotorLeftwardBySteps(int steps); // 左回り前
    void rotateMotorRightwardBySteps(int steps); // 右回り前
    void rotateMotorLeftBackBySteps(int steps); // 左回り後ろ
    void rotateMotorRightBackBySteps(int steps); // 右回り後ろ
    void rotateMotorLeftHalfForwardRotation(); // 左回り前半回転
    void rotateMotorRightHalfForwardRotation(); // 右回り前半回転
    void rotateMotorLeftHalfBackRotation(); // 左回り後半回転
    void rotateMotorRightHalfBackRotation(); // 右回り後半回転
    void rotateMotorChangeDirection(); // 方向を変える
    void moveSteppingMotor(int sirial_data, int steps); // モーターを動かす
};

#endif // __STEPPING_MOTOR__