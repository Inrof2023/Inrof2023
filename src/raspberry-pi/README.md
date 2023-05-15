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

### VSCodeでSSH繋がらなくなったら
たぶん, 同じネットワークに複数のラズパイが繋がってるとき.
`~/.ssh/config`のHostNameをその時のラズパイのipアドレスに変更する

ラズパイのipアドレスの確認方法 \
wlan0のinetの部分がipアドレス（この場合だと192.168.0.7）
```
raspberry@raspberrypi:~ $ ifconfig
eth0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether e4:5f:01:0c:80:64  txqueuelen 1000  (イーサネット)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (ローカルループバック)
        RX packets 23007  bytes 7624633 (7.2 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 23007  bytes 7624633 (7.2 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.7  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::3840:eccc:7fc2:666  prefixlen 64  scopeid 0x20<link>
        ether e4:5f:01:0c:80:65  txqueuelen 1000  (イーサネット)
        RX packets 57260  bytes 57318239 (54.6 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 30540  bytes 7867860 (7.5 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

自分のパソコンで`~/.ssh`に移動する
```
cd ~/.ssh/
```

configファイルのHostNameをさっき調べたIPアドレスに書き換える
```
Host raspberry-raspberry-pi
  HostName raspberrypi.local //ここをipアドレスに変更する
  User raspberry
  IdentityFile ~/.ssh/id_ed25519%  
```

### 参考サイト 
- 全体の流れの参考 \
https://qiita.com/nlog2n2/items/1d1358f6913249f3e186

- configファイルはこちらを参考\
https://hotsmmrblog.com/remote_vscode_to_raspberry_pi/

- 謎警告の解説 \
https://www.niandc.co.jp/tech/20150729_2464/