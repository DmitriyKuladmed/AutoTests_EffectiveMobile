FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps

COPY tests ./tests
COPY pytest.ini ./pytest.ini

ENV BASE_URL=https://effective-mobile.ru/

CMD ["pytest"]

