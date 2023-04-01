# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10.0
# Keeps Python from generating .pyc files in the container
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN mkdir /Botator
RUN mkdir /Botator/code
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /Botator/code
COPY ./code /Botator/code
WORKDIR /Botator/code/

# Create database folder and files (otherwise it will crash)
RUN mkdir /Botator/database
RUN touch /Botator/database/data.db
RUN touch /Botator/database/premium.db
RUN chown -R appuser /Botator/database

RUN mkdir /Botator/database/google


USER appuser
CMD ["python", "code.py"]
