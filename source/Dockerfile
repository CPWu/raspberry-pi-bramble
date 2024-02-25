# Base Image
FROM python:3.9-slim-buster

# Copy the files into a directory within image.
WORKDIR /app

# Copy the requirements file and ensure dependencies are installed
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

# Copy othe contents of the current working directory 
COPY . .

# Set the port where container is running
EXPOSE 5000

# Set commands that are run when image starts as container
CMD ["flask", "run", "--host", "0.0.0.0"]