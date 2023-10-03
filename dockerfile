# Use the Python Alpine base image
FROM python:3.9-alpine

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by dlib
RUN apk update && apk add --no-cache --virtual .build-deps \
    build-base \
    cmake \
    libjpeg-turbo-dev \
    linux-headers \
    && apk add --no-cache \
    libjpeg-turbo \
    && pip install --no-cache-dir dlib

# Copy the project files to the container's working directory
COPY . /app

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose both ports used by the Flask server and other scripts
EXPOSE 8000 8080

# Start the Flask server, start_camera.py, and start_processing.py
CMD ["sh", "-c", "python start_streaming.py & python server.py  & python facerec_ipcamera_knn.py & wait"]
