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

## settings.jsonにIDEのパスなどを記載する
ネットと違ってIDEのファイル名が違うので注意する.（キレそう）
```
"arduino.analyzeOnOpen": true,
"arduino.analyzeOnSettingChange": true,
"arduino.clearOutputOnBuild": false,
"arduino.defaultBaudRate": 9600,
"arduino.disableIntelliSenseAutoGen": false,
"arduino.disableTestingOpen": false,
"arduino.enableUSBDetection": true,
"arduino.logLevel": "info",
"arduino.openPDEFiletype": false,
"arduino.skipHeaderProvider": false,
"arduino.useArduinoCli": true,
"C_Cpp.intelliSenseEngine": "Tag Parser"
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
