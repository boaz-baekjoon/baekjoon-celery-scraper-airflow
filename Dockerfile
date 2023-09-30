# Start from the Airflow image
FROM apache/airflow:2.6.2

# # Change to the root user to install packages
# USER root

# # Copy your requirements file into the Docker container
# COPY requirements.txt /requirements.txt

# # Ensure the directory exists and has the correct permissions
# RUN mkdir -p /opt/airflow/data && chown -R airflow: /opt/airflow/data

# # Change back to the airflow user
# USER airflow

# # Install the Python packages

# # Install additional Python packages if provided
# ARG _PIP_ADDITIONAL_REQUIREMENTS=""
# RUN if [ -n "$_PIP_ADDITIONAL_REQUIREMENTS" ]; then pip install $_PIP_ADDITIONAL_REQUIREMENTS; fi

# Use root user for setting up directories and permissions
USER root

# # Ensure directories exist
# RUN mkdir -p /opt/airflow/dags \
#     && mkdir -p /opt/airflow/logs \
#     && mkdir -p /opt/airflow/plugins \
#     && mkdir -p /opt/airflow/data

RUN apt update && apt-get install sudo -y \
    && echo 'airflow ALL=NOPASSWD: ALL' >> /etc/sudoers
    && apt install -y inetutils-ping

# Copy the current directory's content to the image
COPY . /opt/airflow/

# Change ownership for specified directories to the airflow user and group
RUN chown -R airflow: /opt/airflow/dags \
    && chown -R airflow: /opt/airflow/logs \
    && chown -R airflow: /opt/airflow/plugins \
    && chown -R airflow: /opt/airflow/data

# Grant full permissions for the airflow user for specified directories
RUN chmod -R 777 /opt/airflow/dags \
    && chmod -R 777 /opt/airflow/logs \
    && chmod -R 777 /opt/airflow/plugins \
    && chmod -R 777 /opt/airflow/data

RUN pip uninstall asyncio

RUN usermod -aG docker airflow

# Switch back to the airflow user for subsequent operations
USER airflow

RUN pip install -r /requirements.txt