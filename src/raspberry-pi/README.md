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

### 謎エラーの対処法
IPアドレスが同じでサーバが別になっている場合は下のような警告が出る
```
shibatakeigo@shibatakeigonoMacBook-Air .ssh % ssh -i id_ed25519 raspberry@raspberrypi.local 
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ED25519 key sent by the remote host is
SHA256:0ppjbAaJ9Uxk1U/k8YEvwUcKXKPS0aYLBnhG3II8Se0.
Please contact your system administrator.
Add correct host key in /Users/shibatakeigo/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in /Users/shibatakeigo/.ssh/known_hosts:2
Host key for raspberrypi.local has changed and you have requested strict checking.
Host key verification failed.
```

解決方法は, サーバの前の情報を削除する
```
ssh-keygen -R raspberrypi.local
```

### 参考サイト 
- 全体の流れの参考 \
https://qiita.com/nlog2n2/items/1d1358f6913249f3e186

- configファイルはこちらを参考\
https://hotsmmrblog.com/remote_vscode_to_raspberry_pi/

- 謎警告の解説 \
https://www.niandc.co.jp/tech/20150729_2464/