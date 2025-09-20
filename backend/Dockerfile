# The docker-compose.[environment].yaml file used will determine
# which of these stages are built and run, based on the 
# "build target" setting for the api service.

# Base: ---------------------------------------------------------
FROM python:3.10-slim AS base 

# Prevent Python from buffering logs and writing .pyc files
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /backend


# Local/Development ONLY: Run the dev server ---------------------
FROM base AS local

# Install Python dependencies for development environment
# requirements-dev.txt includes additional dev-related libraries 
# that handle linting, testing, debugging, etc.
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy Django project code
COPY . .

# Expose the Django api port
EXPOSE 8000

# Run the Django dev server in a local setup
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]


# Production ONLY: Run the gunicorn/wsgi server -------------------
FROM base AS production

# Install Python dependencies for production environment
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project code
COPY . .

# Expose the Django api port
EXPOSE 8000

# Run the Django server using gunicorn/wsgi for production
CMD ["gunicorn", "resumai.wsgi:application", "--bind", "0.0.0.0:8000"]
