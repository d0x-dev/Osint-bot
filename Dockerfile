# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything into container
COPY . /app

# Install dependencies (if you have requirements.txt)
# RUN pip install -r requirements.txt

# Run your Python file
CMD ["python", "app.py"]
