FROM debian:jessie
MAINTAINER Maksim Ekimovskii <ekimovsky.maksim@gmail.com>

RUN apt-get update && apt-get install -y \
    gcc \
    libev4 \
    python2.7 \
    python2.7-dev \
    python-setuptools \
    git \
    make

# for MessagesSource
EXPOSE 58000

# for WebSockets server
EXPOSE 59999

# Setup RocketWS
RUN easy_install pip && \
    pip install virtualenv && \
    git clone https://github.com/prawn-cake/RocketWS.git /opt/rocketws

WORKDIR /opt/rocketws
RUN make env


# Run command is `docker run -i -t -d -p 58000:58000 -p 59999:59999 prawncake/rocketws make run_bg`