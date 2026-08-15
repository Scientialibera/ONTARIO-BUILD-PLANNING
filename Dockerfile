FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY pyproject.toml ./
COPY api/ api/
COPY domain/ domain/
COPY services/ services/
RUN pip install --no-cache-dir .
COPY frontend/ frontend/
COPY data/sample/ data/sample/
EXPOSE 8080
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
