# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /

# Install git
RUN apt-get update && apt-get install -y git

# clone the repo and install the requirements

RUN git clone https://github.com/SilverSix311/freya.git

WORKDIR /freya

RUN pip install -r requirements.txt

# run the bot
CMD ["python", "main.py"]