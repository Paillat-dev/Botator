# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-bookworm
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
# Turns off pyc files
ENV PYTHONDONTWRITEBYTECODE=1

ENV TZ=Europe/Paris
# Install pip requirements
WORKDIR /Botator
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /Botator
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
USER appuser
CMD ["python", "main.py"]