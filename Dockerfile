FROM python:3.11-bookworm

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1


# we move to the app folder and run the pip install command
WORKDIR /app

# we copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install pip requirements
RUN pip install -r requirements.txt


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5574 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# We copy the rest of the codebase into the image
COPY . /app

# We run the application
CMD ["python", "main.py"]
