FROM ubuntu:latest

RUN apt -y update 
RUN apt -y upgrade
RUN apt install -y python3.10
RUN apt install -y python3-pip

# シリアル通信用のライブラリ
RUN pip install pyserial