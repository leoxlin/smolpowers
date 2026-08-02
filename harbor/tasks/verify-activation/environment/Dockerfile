FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash agent

COPY . /tmp/environment/

RUN mkdir -p /app /opt/fixture \
    && cp -a /tmp/environment/fixture/. /app/ \
    && cp -a /tmp/environment/fixture/. /opt/fixture/

RUN git -C /app init -q \
    && git -C /app config user.name "Smolpowers Activation" \
    && git -C /app config user.email "activation@example.invalid" \
    && git -C /app add . \
    && git -C /app commit -qm "test: initialize activation fixture" \
    && chown -R agent:agent /app \
    && rm -rf /tmp/environment

WORKDIR /app
USER agent
