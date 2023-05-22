#ifndef __STEPPING_MOTOR__ 
#define __STEPPING_MOTOR__

//ステッピングモーター左
#define DIR_LEFT 4
#define STEP_LEFT 5
//ステッピングモーター右
#define DIR_RIGHT 6
#define STEP_RIGHT 7

// 方向を表す列挙体
enum class Direction {
  FORWARD,
  BACKWARD,
  LEFTWORD,
  RIGHTWORD
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
    void rotateMotorLeftwardBySteps(int steps); // 左回り
    void rotateMotorRightwardBySteps(int steps); // 右回り
    void moveSteppingMotor(int sirial_data, int steps); // モーターを動かす
};

#endif // __STEPPING_MOTOR__