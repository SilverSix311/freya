# syntax=docker/dockerfile:1

FROM ubuntu:20.04

WORKDIR /

# Install git python3 and pip
RUN apt-get update && apt-get install -y git python3 python3-pip

# clone the repo and install the requirements

RUN git clone https://github.com/SilverSix311/freya.git

WORKDIR /freya

RUN pip install -r requirements.txt

# run the bot
CMD ["python", "main.py"]
