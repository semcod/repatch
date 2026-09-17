FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY repatch ./repatch

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[server]"

EXPOSE 8000

CMD ["uvicorn", "repatch.dev_server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
