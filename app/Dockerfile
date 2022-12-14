FROM python:3.8-slim-buster

WORKDIR /app
RUN apt-get update &&\
    apt-get install -y curl 
RUN curl "http://172.21.100.253:3000/qdt/Network/raw/branch/master/apt-interal.public.gpg.key" | apt-key add - && \
    echo "deb [arch=amd64] http://172.21.100.15:8081/repository/apt-internal bionic main # also provide hosted packages" > /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://172.21.100.15:8081/repository/apt-proxy bionic main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb [arch=amd64] http://172.21.100.15:8081/repository/apt-proxy bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list 

COPY requirements.txt requirements.txt
RUN apt-get install ffmpeg libsm6 libxext6  -y  && \
    pip3 install --upgrad pip && \
    pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "./app.py"]
