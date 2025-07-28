"""
Endpoints for the optimization service API
"""
import pyarrow as pa
from fastapi import Request
from fastapi import FastAPI, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from controller.endpoints import Endpoint
from utils.api_utils import *
from utils.dict_to_pa_table import dict_to_pa_table, unpack_pa_table_dict

app = FastAPI()
endpoint = Endpoint()

@app.post("/computeJSON")
async def compute_json(request: Request) -> Response:
    """Execute computation using a model and data, entry and return in JSON format.

    Args:
        request (Request): request object with model info.

    Returns:
        Response: response object with results and/or messages.
    """
    try:
        raw = await request.json()
        table = dict_to_pa_table(raw)
        success, result = endpoint.compute(payload=table)
        return_data = unpack_pa_table_dict(result)
        if success:
            return JSONResponse(
                content = jsonable_encoder(return_data),
                status_code = status.HTTP_200_OK,
                media_type= "application/json"
            )
        return JSONResponse(
            content = jsonable_encoder(return_data),
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type= "application/json"
        )
    except Exception as e:
        return JSONResponse(
            content = jsonable_encoder({
                "error_message": f"{type(e).__name__}: {str(e)}"
            }),
            status_code = status.HTTP_400_BAD_REQUEST,
            media_type= "application/vnd.apache.arrow.stream"
        )

@app.post("/compute")
async def compute(request: Request) -> Response:
    """Execute computation using a model and data.

    Args:
        request (Request): request object with model info.

    Returns:
        Response: response object with results and/or messages.
    """
    try:
        raw = await request.body()
        reader = pa.ipc.open_stream(raw)
        table = reader.read_all()
        success, result = endpoint.compute(payload=table)
        ipc_bytes = write_table_to_ipc_bytes(result)
        if success:
            return Response(
                content = ipc_bytes,
                status_code = status.HTTP_200_OK,
                media_type= "application/vnd.apache.arrow.stream"
            )
        return Response(
            content = ipc_bytes,
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type= "application/vnd.apache.arrow.stream"
        )
    except (ValueError, KeyError) as e:
        response = pa.RecordBatch.from_pydict({
                "error_message": [f"{type(e).__name__}: {str(e)}"]
            })
        ipc_bytes = write_table_to_ipc_bytes(response)
        return Response(
            content = ipc_bytes,
            status_code = status.HTTP_400_BAD_REQUEST,
            media_type= "application/vnd.apache.arrow.stream"
        )
