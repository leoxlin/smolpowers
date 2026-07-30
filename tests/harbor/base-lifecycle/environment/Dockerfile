FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git jq ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipx==1.16.1

RUN useradd --create-home --shell /bin/bash agent

COPY fixture/ /app/
COPY fixture/ /opt/fixture/
COPY plugin/ /opt/smolpowers/
COPY verify_finished.py /opt/verify_finished.py

RUN git -C /opt/smolpowers init -q \
    && git -C /opt/smolpowers config user.name "Smolpowers Plugin Integration" \
    && git -C /opt/smolpowers config user.email "integration@example.invalid" \
    && git -C /opt/smolpowers add . \
    && git -C /opt/smolpowers commit -qm "test: stage plugin" \
    && chown -R agent:agent /opt/smolpowers

RUN git -C /app init -q \
    && git -C /app config user.name "Smolpowers Integration" \
    && git -C /app config user.email "integration@example.invalid" \
    && git -C /app add . \
    && git -C /app commit -qm "test: initialize base fixture" \
    && chown -R agent:agent /app \
    && chmod 444 /opt/verify_finished.py

WORKDIR /app
USER agent
