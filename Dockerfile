# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /own_video

# Copy the current directory contents into the container at /app
COPY . /own_video

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main)api.py when the container launches
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "80"]