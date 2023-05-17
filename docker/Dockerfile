FROM ubuntu:latest

RUN apt -y update 
RUN apt -y upgrade
RUN apt install -y python3.10
RUN apt install -y python3-pip

# シリアル通信用のライブラリ
RUN pip install pyserial

# ardiuno cliをインストール
RUN apt install -y wget
RUN wget -qO arduino-cli.tar.gz https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz
RUN tar xf arduino-cli.tar.gz -C /usr/local/bin arduino-cli
RUN mv arduino-cli /usr/local/bin
RUN rm -rf arduino-cli.tar.gz

# ardiuno-cliからライブラリをインストール
RUN arduino-cli lib install Servo

# USBポートから書き込みできるようにしたいね