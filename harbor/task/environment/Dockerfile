FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git jq ripgrep \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash agent

COPY . /tmp/environment/

RUN mkdir -p /app /opt/fixture \
    && cp -a /tmp/environment/fixture/. /app/ \
    && cp -a /tmp/environment/fixture/. /opt/fixture/

RUN if [ -f /tmp/environment/verify_finished.py ]; then \
        cp /tmp/environment/verify_finished.py /opt/verify_finished.py \
        && chmod 444 /opt/verify_finished.py; \
    fi

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN git -C /app init -q \
    && git -C /app config user.name "Smolpowers Integration" \
    && git -C /app config user.email "integration@example.invalid" \
    && git -C /app add . \
    && git -C /app commit -qm "test: initialize fixture" \
    && chown -R agent:agent /app \
    && rm -rf /tmp/environment

WORKDIR /app
USER agent
