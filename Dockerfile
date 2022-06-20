FROM python:3.7

RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget
RUN apt-get update --fix-missing && \
    apt-get upgrade -y

RUN apt-get update && apt-get install ffmpeg -y
RUN apt-get install -y libssl-dev build-essential automake pkg-config libtool libffi-dev libgmp-dev libyaml-cpp-dev
RUN apt-get install -y libsecp256k1-dev

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

EXPOSE 8080

WORKDIR /identSawtooth

COPY . /identSawtooth

WORKDIR /identSawtooth/backend

# CMD gunicorn -w 1 main:app --bind 0.0.0.0:8080 --worker-class aiohttp.worker.GunicornUVLoopWebWorker --timeout 120 --graceful-timeout 120
CMD python3 main.py