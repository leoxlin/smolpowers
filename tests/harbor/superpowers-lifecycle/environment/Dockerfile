FROM python:3.14-slim

ARG TARGETARCH
ARG YQ_VERSION=v4.53.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git ripgrep \
    && case "$TARGETARCH" in \
         amd64) yq_arch=amd64 ;; \
         arm64) yq_arch=arm64 ;; \
         *) echo "unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
       esac \
    && curl -fsSL \
      "https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_${yq_arch}" \
      -o /usr/local/bin/yq \
    && chmod 755 /usr/local/bin/yq \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash agent

COPY fixture/ /app/
COPY verify_finished.py /opt/verify_finished.py

RUN git -C /app init -q \
    && git -C /app config user.name "Smolpowers Integration" \
    && git -C /app config user.email "integration@example.invalid" \
    && git -C /app add . \
    && git -C /app commit -qm "test: initialize mixed-skill fixture" \
    && chown -R agent:agent /app \
    && chmod 444 /opt/verify_finished.py

WORKDIR /app
USER agent
