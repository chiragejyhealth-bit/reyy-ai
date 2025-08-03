# ---------- Base Python image ----------
FROM python:3.12-slim

WORKDIR /app

# ---------- OS packages ----------
#  * Xvfb + X libs let Chrome run head-ful
#  * build-essential kept because your image already needed it
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget gnupg ca-certificates curl \
        xvfb libgtk-3-0 libdbus-glib-1-2 libnss3 libxss1 \
        libasound2 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
        libxi6 libxtst6 libxrandr2 libu2f-udev libvulkan1 \
        fonts-liberation build-essential && \
    # ---- Google-Chrome stable repo ----
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | \
        gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ---------- Python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- App code & runtime dirs ----------
COPY . .
RUN mkdir -p data/audio data/images data/transcripts responses/pdf

# ---------- Xvfb + Chrome runtime settings ----------
ENV DISPLAY=:99
ENV XVFB_WHD=1920x1080x24
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# ---------- Entrypoint ----------
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
