FROM python:3.12-slim-bookworm
WORKDIR /app

# TgCrypto is a C extension; the slim base image has no compiler, so pip
# falls back to building it from source and fails without these. If a
# prebuilt wheel exists for your platform this is a no-op, but it's cheap
# insurance either way.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD python3 main.py
