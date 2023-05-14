# raspberry-pi
raspberry-pi用のプログラム

# raspberry-piへSSH接続
## 公開鍵暗号方式で設定するのが無難
### 参考サイト 
https://tenshoku-careerchange.jp/column/1031/

## VSCodeのRemotoSSHで接続
公開鍵暗号方式でSSH接続できるようになったらVSCodeでも接続できる.
### configの注意点
同じネットワークに複数台ラズパイをつなぐとホスト名が被ってしまうことがあるので, その時はconfigのHostをラズパイのipアドレスに変更する必要がある. ラズパイのホスト名を変えてしまうのも一つの手かもしれない.デフォルトのホスト名は`raspberrypi.local`

### 参考サイト 
- 全体の流れの参考 \
https://qiita.com/nlog2n2/items/1d1358f6913249f3e186

- configファイルはこちらを参考\
https://hotsmmrblog.com/remote_vscode_to_raspberry_pi/