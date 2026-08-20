FROM python:3.12-slim

# Аргументы для корпоративных сертификатов и индекса PyPI (Транснефть)
ARG NEXUS_CERT=""
ARG PYPI_INDEX_URL="https://pypi.org/simple/"

# Установка корпоративного сертификата при пробросе NEXUS_CERT
RUN if [ -n "$NEXUS_CERT" ]; then \
      echo "$NEXUS_CERT" >> /usr/local/share/ca-certificates/nexus.crt && \
      update-ca-certificates; \
    fi

WORKDIR /app

# Установка зависимостей
COPY pyproject.toml .
RUN pip install --index-url $PYPI_INDEX_URL --no-cache-dir .

# Копирование исходного кода и рантайм-конфигурации
COPY src/ src/
COPY configs/ configs/

EXPOSE 8000

CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
