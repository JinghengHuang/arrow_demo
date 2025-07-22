# Use an official Python runtime as a parent image
FROM ubuntu:latest
SHELL ["/bin/bash", "-c"]
# Set environment variables for configuration
RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        curl \
        wget \
        build-essential

# Install latest g++ from Debian repositories
RUN apt-get install -y g++

# Install Python 3.12 via deadsnakes (for Ubuntu) or from source (for Debian)
# Debian stable does not have python3.12 prebuilt yet, so build from source

RUN apt-get install -y \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libdb5.3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    uuid-dev \
    python3.12-venv \
    && cd /usr/src \
    && wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz \
    && tar xzf Python-3.12.3.tgz \
    && cd Python-3.12.3 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make altinstall

# Verify installations
RUN g++ --version && python3.12 --version

# Set default python if desired
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.12 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Set env paths
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1
ENV PROJ_HOME="/usr/src/app"
ENV JULIA_VERSION="1.11.5"
ENV POETRY_VERSION="2.1.3"
ENV IPOPT_VERSION="3.14.0"
ENV PATH="root/.local/bin:$PATH"
ENV PYTHONPATH="/usr/src/app"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"

RUN ./scripts/envSetup.sh

# Make port 80 available to the world outside this container (Optional, only for web apps)
EXPOSE 8000

# Define environment variable (optional)
ENV NAME venv

# Check python address
RUN source /etc/profile.d/myenv.sh && whereis python
# Run app.py when the container launches
CMD ["bash", "-c", "source /etc/profile.d/myenv.sh && ./scripts/startServer.sh"]