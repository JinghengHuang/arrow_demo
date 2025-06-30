# Apache Flight gRPC Server / FastAPI server gateway

A framework for Apache Flight gRPC Server / FastAPI server gateway

Used for the Cobra Arrow Project, related to [OpenCobra toolbox project](https://github.com/opencobra/cobratoolbox)

Python >= 3.10 Recommended

## To create virtual environment

```bash
python -m venv .venv
.venv/Scripts/activate
```

## To install dependency

```bash
pip install -r requirements.txt
```

## To start all server instances

```bash
python run_all.py
```

## To start all engine service instances

```bash
python run_engine_service.py
```

## To start gateway service instances

```bash
python run_server.py
```

## Docker

Use `server.dockerfile` to create container for gateway server service;

Use `engine.dockerfile` to create container for engine services.