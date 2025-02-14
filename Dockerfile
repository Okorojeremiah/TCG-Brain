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

# Expose the port your app runs on (Flask defaults to 5000)
EXPOSE 5000

# Define environment variable for Flask 
ENV FLASK_APP=run.py

# Run the application (binding to 0.0.0.0 makes it accessible externally)
CMD ["flask", "run", "--host=0.0.0.0"]
