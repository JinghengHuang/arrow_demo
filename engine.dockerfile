# Use an official Python runtime as a parent image
FROM ubuntu:latest

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
ENV JULIA_VERSION=1.10.3

# Download and install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.10/julia-$JULIA_VERSION-linux-x86_64.tar.gz && \
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
RUN rm -rf .VIRTUAL_ENV
ENV VIRTUAL_ENV=/usr/src/app/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

RUN cd ./service/optimization_service/julia
RUN julia -e 'using Pkg; Pkg.instantiate()'
RUN cd /usr/src/app

# Make port 80 available to the world outside this container (Optional, only for web apps)
EXPOSE 8101
EXPOSE 65432

# Define environment variable (optional)
ENV NAME venv

# Run app.py when the container launches
CMD ["python", "./run_engine_service.py"]