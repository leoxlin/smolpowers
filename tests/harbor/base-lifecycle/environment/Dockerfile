FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git jq ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash agent

COPY fixture/ /app/
COPY fixture/ /opt/fixture/
COPY plugin/ /opt/smolpowers/
COPY verify_finished.py /opt/verify_finished.py

RUN git -C /app init -q \
    && git -C /app config user.name "Smolpowers Integration" \
    && git -C /app config user.email "integration@example.invalid" \
    && git -C /app add . \
    && git -C /app commit -qm "test: initialize base fixture" \
    && chown -R agent:agent /app \
    && chmod 444 /opt/verify_finished.py

WORKDIR /app
USER agent
