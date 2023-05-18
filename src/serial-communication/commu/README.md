## Arduino -> Raspberrypiへのシリアル通信

### MotorService
#### メソッド
- `driveMotor`\
    ラズパイから受け取ったバイト列を解析して, その通りにモータ（ステッピング, サーボ, DC）を動かす
#### コンストラクタ
- `MotorService(SteppingMotor stepping_motor)`\
    引数に`SteppingMotor`, `ServoMotor`, `DCMotor`をとる

### CommunicationService
#### メソッド
- `send` \
    フォトリフレクタからの値をラズパイに送る \
    引数
    - line: int型の配列で4つのフォトリフレクタの値が左から順に入っている\
- `receive`\
    ラズパイからのデータを受信する\
    戻り値
    - data: charでラズパイから受信したデータを返す

### SteppingMotor
#### メソッド
- `rotateMotorForwardBySteps` \
    指定したステップだけ前進する
- `rotateMotorBackwardBySteps` \
    指定したステップだけ後退する
- `rotateMotorLeftwardBySteps` \
    指定したステップだけ左周りする
- `rotateMotorRightwardBySteps` \
    指定したステップだけ右回りする
- `moveSteppingMotor` \
    ラズパイから受け取ったビットで動く

### ServoMotor
未実装

### DCMotor
未実装