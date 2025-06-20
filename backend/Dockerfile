FROM --platform=linux/amd64 python:3.11.0-slim

WORKDIR /usr/backend

# Set up Python behaviour
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv

# Switch on virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the server port
EXPOSE 8000

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt

# Copy all files
COPY . .

# Copy entrypoint.sh for auto connection with account_db service
COPY ./entrypoint.sh .
RUN chmod +x /usr/backend/entrypoint.sh

# Execute entrypoint.sh
ENTRYPOINT ["/usr/backend/entrypoint.sh" ]

# Start up the backend server
CMD uvicorn src.main:backend_app --reload --workers 4 --host 0.0.0.0 --port 8000
