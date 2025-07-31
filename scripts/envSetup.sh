#!/bin/bash
export PROJ_HOME=$PWD
export PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1
export JULIA_VERSION="1.11.5"
export POETRY_VERSION="2.1.3"
export PYTHONUNBUFFERED=1
export IPOPT_VERSION="3.14.0"
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=$PWD

echo "Start installing dependencies..."
echo $PROJ_HOME
echo "Installing Solvers(GLPK, IPOPT, HIGHS)"
apt-get update && apt-get install -y curl
# GLPK
apt-get install -y libglpk-dev glpk-utils
glpsol --version
# IPOPT
apt-get install -y gfortran  gcc  g++  make  wget  unzip  pkg-config  liblapack-dev  libblas-dev  libtool  coinor-libipopt-dev  build-essential  git  cmake  python3-dev  python3-pip  libopenblas-dev  libmumps-seq-dev  libmetis-dev
mkdir /opt/ipopt && cd /opt/ipopt
git clone https://github.com/coin-or/Ipopt.git
cd Ipopt
mkdir ThirdParty && cd ThirdParty
git clone https://github.com/coin-or-tools/ThirdParty-Mumps.git
cd ThirdParty-Mumps && ./get.Mumps
./configure
make && make install
cd /opt/ipopt/Ipopt/ThirdParty
git clone https://github.com/coin-or-tools/ThirdParty-ASL.git
cd ThirdParty-ASL && ./get.ASL
./configure
make && make install
cd /opt/ipopt/Ipopt
mkdir build && cd build
# Not using HSL for testing environment, because it requires license and stuff
../configure --with-mumps-cflags=-I/usr/include/mumps_seq --with-mumps-lflags=-ldmumps_seq --without-hsl
make
make test
make install

ls /usr/local/lib
find /usr/local/lib -name libipoptamplinterface.*
find / -name ipopt
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
# Highs
cd /opt
mkdir highs && cd highs
git clone https://github.com/ERGO-Code/HiGHS.git && cd HiGHS
cmake -S . -B build
cmake --build build
cd build && ctest
PATH=$PATH:/opt/highs/HiGHS/build/bin
# Julia
echo "Installing Julia"
cd /tmp
echo https://julialang2eastus2.blob.core.windows.net/julialang2/bin/linux/x64/${JULIA_VERSION:0:4}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz
wget https://julialang2eastus2.blob.core.windows.net/julialang2/bin/linux/x64/${JULIA_VERSION:0:4}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz
tar -xzf julia-${JULIA_VERSION}-linux-x86_64.tar.gz
mv julia-${JULIA_VERSION} /opt/julia
ln -s /opt/julia/bin/julia /usr/bin/julia
julia --version
cd $PROJ_HOME
julia --project=./src/service/optimization_service/julia -e "import Pkg; Pkg.instantiate()"

# Poetry
echo "Installing Poetry"
cd $PROJ_HOME
echo $PROJ_HOME
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
poetry install --no-interaction  --no-ansi --no-root
export PYTHONPATH=$PWD

echo "export LD_LIBRARY_PATH=\"$LD_LIBRARY_PATH:/usr/local/lib\"" >> /etc/profile.d/myenv.sh
echo "export PATH=\"$PATH:/opt/highs/HiGHS/build/bin:$HOME/.local/bin\"" >> /etc/profile.d/myenv.sh
echo "export PYTHONPATH=$PWD" >> /etc/profile.d/myenv.sh