FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    git \
    imagemagick

RUN POLICY_FILE=$(find /etc -name "policy.xml") && \
    sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PS"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PS2"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PS3"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="EPS"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="PDF"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="XPS"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="MVG"/<!-- & -->/' "$POLICY_FILE" && \
    sed -i 's/<policy domain="coder" rights="none" pattern="TEXT"/<!-- & -->/' "$POLICY_FILE"

WORKDIR /app

COPY requirements.txt .
COPY assets/font.ttf assets/font.ttf
COPY assets/expressions/ assets/expressions/
COPY assets/intros/ assets/intros/
COPY assets/musics/ assets/musics/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir git+https://github.com/openai/whisper.git
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install moviepy[full]

COPY . .
