#!/bin/bash
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
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
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
wget https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_VERSION:0:4}/julia-$JULIA_VERSION-linux-x86_64.tar.gz
tar -xzf julia-$JULIA_VERSION-linux-x86_64.tar.gz
mv julia-$JULIA_VERSION /opt/julia
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
poetry config virtualenvs.create true
poetry install --no-interaction --no-root
poetry env list
source `poetry env info --path`/bin/activate
export PYTHONPATH=$PWD