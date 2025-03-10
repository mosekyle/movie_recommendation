FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run as non-root user for better security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]