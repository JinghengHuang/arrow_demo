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
    glpk-utils libglpk-dev glpk-doc \
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

# install julia
# Set JULIA version
ENV JULIA_VERSION=1.11.5

# Download and install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.11/julia-$JULIA_VERSION-linux-x86_64.tar.gz && \
    tar -xvzf julia-$JULIA_VERSION-linux-x86_64.tar.gz && \
    mv julia-$JULIA_VERSION /opt/julia && \
    ln -s /opt/julia/bin/julia /usr/local/bin/julia && \
    rm julia-$JULIA_VERSION-linux-x86_64.tar.gz

# Test Julia
RUN julia --version
# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Set env paths
ENV PROJ_HOME=$PWD
ENV JULIA_VERSION="1.11.5"
ENV POETRY_VERSION="2.1.3"
ENV PYTHONUNBUFFERED=1
ENV IPOPT_VERSION="3.14.0"
ENV PATH="$HOME/.local/bin:$PATH"
ENV PYTHONPATH=$PWD

RUN ./scripts/envSetup.sh

# Make port 80 available to the world outside this container (Optional, only for web apps)
EXPOSE 65432

# Define environment variable (optional)
ENV NAME venv

# Run app.py when the container launches
CMD ["sh", "./scripts/startJulia.sh"]