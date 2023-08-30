FROM debian:bookworm-slim

WORKDIR /app

ADD requirements.txt .

# Doing all this with a debian:bookworm-slim image leads to a ~190MB image.
# With python:3.11 and "pip install -r requirements.txt" you get an image
# that's over 1GB. python:3.11-slim is missing gcc which is needed for ed25519,
# which is required for NKEY / JWT authentication support.
RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    && \
  pip install --break-system-packages -r requirements.txt && \
  apt-get purge -y --auto-remove --purge \
    build-essential \
    python3-dev \
    && \
  find \
    /var/cache/apt \
    /var/cache/ldconfig \
    /var/lib/apt/lists \
    -mindepth 1 -delete && \
  rm -rf /root/.cache

ADD main.py .

CMD ["python3", "main.py"]
