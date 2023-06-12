# arduino
arduino用のプログラム

# 端子
### フォトリフレクタ
- A0: 左
- A1: 真ん中の左
- A2: 真ん中の右
- A3: 右

### サーボモータ
D2

### DCモータ
D3

### ステッピングモーダ左
- D4: DIR
- D5: STEP

### ステッピングモータ右
- D6: DIR
- D7: STEP

# VSCodeでArduinoの開発
だいぶハマったのでメモ
## Arduinoの拡張機能をインストール
インストール自体は普通にする.
下の画面に`Select Board Type`と出るからこれをクリックしてBoard用のドライバをインストールする.（多分一番上をえらべばOK）. Processorを`Old Bootloader`に変更するのを忘れずに.

## ardiuno-cliのインストール
最新版ではVSCodeでIDEを引っ張って来れない. cliをインストールしてそれのパスを通せと怒られるから注意.（割と最近なったみたいだkらネットにこの情報がなかった.）下のコマンドを実行する.（実行するときは`$`を消すことを忘れないように）
```
$ wget http://downloads.arduino.cc/arduino-cli/arduino-cli-0.2.1-alpha.preview-linuxarm.tar.bz2
$ tar xf arduino-cli*
$ mv arduino-cli-0.2.1-alpha.preview-linuxarm arduino-cli
$ sudo mv arduino-cli /usr/local/bin
$ rm -rf arduino-cli-0.2.1-alpha.preview-linuxarm.tar.bz2 
```
ardiuno-cliで使うライブラリをインストール
```
arduino-cli lib install Servo
```

## includeパスの設定
`Inrof2023/.vscode`フォルダの中に`c_cpp_properties.json`を作る.（いい感じにすると自動で作られる）
ここに次の設定を追加する.
ネットの情報と全く違ったのでここでハマった.Arduino関係のライブラリが入っているパスが`/Users/shibatakeigo/Library/Arduino15/libraries/**`に変わっていた.（クソ）\
Arduino IDEのincludeするところにカーソルを長くおくとファイルのパス名が表示されるので, それで確認した.
```
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**",
                "/Users/shibatakeigo/Documents/Arduino/libraries/**",
                "/Users/shibatakeigo/Library/Arduino15/libraries/**"
            ],
            "defines": [],
            "compilerPath": "/usr/bin/gcc",
            "cStandard": "c17",
            "cppStandard": "gnu++17",
            "intelliSenseMode": "linux-gcc-arm64"
        }
    ],
    "version": 4
}
```

### 色々な定格
- サーボモータ \
`MG996R` \
データシート: https://akizukidenshi.com/catalog/g/gM-12534/ \
動作電圧: 4.8V~6.6V
- フォトリフレクタ \
`ＴＰＲ－１０５Ｆ` \
データシート: https://akizukidenshi.com/download/tpr-105f.pdf \
動作電圧: 5V?

