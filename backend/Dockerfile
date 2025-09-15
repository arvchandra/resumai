FROM python:3.10-slim

# Declaere
ARG APP_ENV=production

# Prevent Python from buffering logs and writing .pyc files
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /backend

# Install Python dependencies (based on environment type)
COPY requirements.txt requirements-dev.txt ./
RUN if [ "$APP_ENV" = "local" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy Django project code
COPY . .

# Expose the Django api port
EXPOSE 8000

# Run the Django dev server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
