# Inrof用のプログラム

## Dockerで仮想仮想環境の起動
```
cd docker
docker build -t raspberry .
docker run -it --rm -v ${PWD}/..:/src raspberry bash
```