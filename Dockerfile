FROM debian:jessie
MAINTAINER Maksim Ekimovskii <ekimovsky.maksim@gmail.com>

RUN apt-get update && apt-get install -y \
    libev4 \
    python2.7 \
    python-setuptools \
    git \
    make

EXPOSE 58000  # for MessagesSource
EXPOSE 59999  # for WebSockets server

# Setup RocketWS
RUN pip install virtualenv && \
    git clone https://github.com/prawn-cake/RocketWS.git /opt/rocketws

WORKDIR /opt/rocketws
RUN make env

