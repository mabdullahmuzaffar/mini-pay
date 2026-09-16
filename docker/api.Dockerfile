FROM python:3.12-slim

WORKDIR /app

# Optimize layer build caching strategies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy pristine source files
COPY app/ ./app/

# Enforce secure non-privileged container contexts
RUN useradd -r -u 10001 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
