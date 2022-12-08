FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update &&\
    apt-get install ffmpeg libsm6 libxext6  -y  && \
    pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "./app.py"]
