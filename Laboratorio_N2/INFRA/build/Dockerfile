FROM ubuntu:24.04

LABEL maintainer="Huriviades"
LABEL project="Apis"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        supervisor \
        xz-utils \
        curl \
        git \
        wget \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-pip \
        python3-dev \
        python3-venv \
        python3-cffi \
        python3-brotli \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8000

RUN mkdir -p /var/log/supervisor /etc/supervisor/conf.d

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
