# 通信方法の規約

## Arduino -> raspberrypi
### フォトリフレクタの値
カンマ区切りで四つ 
```
左, 真ん中左, 真ん中右, 右
```

## raspberrypi -> Ardiuno
### ステッピングモータ
4bit表記
- 0000: 止まる
- 0001: 直進
- 0010: 後退
- 0011: 左回り前
- 0100: 右回り前
- 0101: 左回り後ろ
- 0110: 右回り後ろ
- 0111: 左旋回（ボールをゴールに入れる時に必要）
- 1000: 右旋回（ボールをゴールに入れる時に必要）

### サーボ
- 0: デフォルトの位置
- 1: 吸った状態

### DCモータ
- 0: 吸わない
- 1: 吸う

### ライントーレスをするかどうか
- 0: ライントーレスしない（ラズパイが直接制御）
- 1: ライントレースする（Arduinoが制御する）

### ライントレースするときの向き
- 0: 前進
- 1: 後退

### 送り方
上が上位ビット, 下が下位ビット
```
ライントレースをするときの向き(1bit) ライントレースするかどうか(1bit) DCモータ(1bit) サーボ(1bit) ステッピングモータ(4bit)
```

# メモ
シリアル通信の規格を確認\
バイト単位で送った方が無駄がないかも