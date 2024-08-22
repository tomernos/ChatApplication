# Use the latest Python image as the base
FROM python:latest

# Set the working directory inside the container
WORKDIR /python-docker

# Copy the requirements.txt file into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies specified in requirements.txt
RUN yun install python3 -y

# Install the Python dependencies specified in requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 5000

# Define the command to run the Flask application
CMD ["python3", "-m", "my_flask.py", "--host=0.0.0.0"]