FROM python:3.12-slim

ARG UID=1000
ARG GID=1000

RUN groupadd -g "${GID}" appgroup && \
    useradd --create-home --no-log-init -u "${UID}" -g "${GID}" appuser && \
    mkdir -p /app/uploads && \
    chown -R appuser /app/uploads

WORKDIR /app

RUN apt-get update && \
    apt-get install -y curl && \
    pip install --upgrade pip

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER appuser:appgroup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY /app .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]