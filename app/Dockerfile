FROM python:3.11-bookworm

RUN addgroup --system abduvohid && adduser --system --group abduvohid
# Ishchi katalogni sozlash
WORKDIR /media_service

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    libc6 \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libexpat1 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    fonts-liberation \
    netcat-openbsd \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y ffmpeg


RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir playwright && playwright install --with-deps

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /media_service/entrypoint.sh
RUN chmod +x /media_service/entrypoint.sh

COPY . .

RUN chown -R abduvohid:abduvohid /media_service

USER abduvohid

ENTRYPOINT ["sh", "/media_service/entrypoint.sh"]