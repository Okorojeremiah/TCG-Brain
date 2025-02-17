# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

RUN apt-get update && apt-get install -y gcc libpq-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of your application code
COPY . .

EXPOSE 8000

# Run the application 
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tcg-brain:app"]
