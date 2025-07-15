# Apache Flight gRPC Server / FastAPI server gateway

A framework for Apache Flight gRPC Server / FastAPI server gateway

Contains OptArrow processing engine(implemented using Pyomo and Julia) and gateway service for request handling.

Used for the Cobra Arrow Project, related to [OpenCobra toolbox project](https://github.com/opencobra/cobratoolbox)

Python >= 3.12 Recommended

Now integrated with poetry, and can be used to run unit tests. The best practice is to use poetry to handle dependency and environment management.

Currently supported solvers:

    - GLPK (Not supported for QP problems)
    - GUROBI
    - HIGHS
    - IPOPT

Please ensure that the executables for the solvers are properly installed and in the system PATH.

## To create and activate virtual environment

```bash
python -m venv .venv
# On windows
.venv/Scripts/activate
# On Mac/Linux
source .venv/bin/activate
```

## To install dependency

Install `poetry` first. See [Poetry install](https://python-poetry.org/docs/)

```bash
# With poetry
poetry install --no-root
```

## To install new dependency package

```bash
# With poetry
poetry add <dependency-name>
```

Please don't use pip or any other dependency management.

## To start all server instances (engine + gateway)

```bash
sh startAll
```

## To start gateway service instances

```bash
sh startServer
```

## To start python engine service instances

```bash
sh startPyEngine
```

## To start julia engine service instances

```bash
sh startJulia
```

## To run unit tests

Remember to start all the services before running tests, otherwise the tests will fail.

```bash
poetry run pytest
```

## Docker

Alternatatively, Docker can be used to create segregated environments for running all the services in different containers in a production environment. Use `server.dockerfile` to create container for gateway server service.

Docker environment is required. To install Docker, see [Docker install](https://docs.docker.com/engine/install/)

```bash
# In project directory:
docker build -t gateway-server -f server.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host gateway-server
```

Use `py_engine.dockerfile` to create container for pyomo engine services.

```bash
# In project directory:
docker build -t py-engine-server -f py_engine.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host py-engine-server
```

Use `julia_engine.dockerfile` to create container for julia engine services.

```bash
# In project directory:
docker build -t julia-engine-server -f julia_engine.dockerfile .
# Start docker, with network synced with the host.
docker run -d --net=host julia-engine-server
```

## Configure service ports

See `config.yaml` for service ip/port configurations.

If ports are changed, remember to change the Dockerfiles respectively to ensure the right ports are opened.
