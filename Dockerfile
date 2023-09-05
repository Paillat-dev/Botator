# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10.13-slim-bullseye
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
# Install git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*
# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN git clone https://github.com/Paillat-dev/Botator.git
WORKDIR /Botator
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /Botator
USER appuser
CMD ["python", "main.py"]