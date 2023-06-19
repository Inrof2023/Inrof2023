# Inrof用のプログラム

## Dockerで仮想仮想環境の起動
```
cd docker
docker build -t raspberry .
docker run -it --rm -v ${PWD}/..:/src raspberry bash
```

## フォルダの構成
```
├── README.md
├── docker
│   └── Dockerfile
└── src
    ├── arduino 
        それぞれのモータを動かすサンプルコードが置いてある
    ├── raspberry-pi
        ラズパイ用のプログラム
        この中のprogramディレクトリのcommunication.pyが実際に使ったプログラム
    └── serial-communication
        この中のcommuのcommu.inoが実際に使ったプログラム
```
