FROM python:3.10-slim

# Prevent Python from buffering logs and writing .pyc files
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /backend

# Install Python dependencies
COPY requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project code
COPY . .

# Expose the Django api port
EXPOSE 8000

# Run the Django dev server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
