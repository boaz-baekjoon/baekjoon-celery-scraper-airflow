# Stage 1: Build environment with python:3.10-slim-buster
FROM python:3.10-slim-buster AS builder

# Set the working directory
WORKDIR /build

# Install PostgreSQL development files and other build dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the build directory
COPY . .

# Stage 2: Deploy environment with python:3.10-slim-buster
FROM python:3.10-slim-buster AS deployer

# Install only the runtime library for PostgreSQL
RUN apt-get update && \
    apt-get install -y libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the environment to use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the built application from the builder stage
COPY --from=builder /build /app

# Set the working directory
WORKDIR /app

EXPOSE 6800

RUN chmod +x run_script.sh

# Run command
#CMD ["run_script.sh"]