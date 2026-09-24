# ==========================================
# Django backend (replaces the Spring Boot image)
# ==========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Same port the Spring Boot service used, so the k8s Service and Nginx stay unchanged
EXPOSE 8090

CMD ["gunicorn", "college_project.wsgi:application", "--bind", "0.0.0.0:8090", "--workers", "2", "--access-logfile", "-"]
