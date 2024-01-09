# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    unzip \
    wget \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/svalluri93/nseit-media-analytics.git .

RUN pip3 install -r requirements.txt

RUN unzip ./python-client-generated.zip

RUN pip3 install ./python-client-generated/python-client/

RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip
RUN wget https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.zip
RUN mkdir ./.EasyOCR
RUN mkdir ./.EasyOCR/model
RUN unzip english_g2.zip -d ./.EasyOCR/model
RUN unzip craft_mlt_25k.zip -d ./.EasyOCR/model

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]