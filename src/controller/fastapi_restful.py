"""
Endpoints for the optimization service API
"""
import pyarrow as pa
from fastapi import Request
from fastapi import FastAPI, status
from fastapi.responses import Response
from controller.endpoints import Endpoint
from utils.api_utils import *

app = FastAPI()
endpoint = Endpoint()

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
