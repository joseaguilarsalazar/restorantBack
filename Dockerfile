# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Expose port
EXPOSE 8000

# Run migrations, collect static files, create superuser, and start Daphne
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python create_superuser.py && daphne -b 0.0.0.0 -p 8000 ProyectoBack.asgi:application"]
