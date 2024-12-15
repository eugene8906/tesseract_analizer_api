FROM python:3.12


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus \
    libtesseract-dev \
    wget \
    postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /file_analyzer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod a+x /file_analyzer/docker/*.sh

CMD ["uvicorn", "app.main:app", "--host 0.0.0.0", "--port 8000", "--reload"]

