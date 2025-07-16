"""
Endpoints for the optimization service API
"""
import pyarrow as pa
from fastapi import Request
from fastapi import FastAPI, status
from fastapi.responses import Response
from controller.endpoints import Endpoint

app = FastAPI()
endpoint = Endpoint()

@app.post("/compute")
async def compute(request: Request):
    """
    Execute computation using a model and data, either from ID or inline.
    :param request: Request object containing the payload
    :return: Response with result metadata and output
    """
    try:
        raw = await request.body()
        reader = pa.ipc.open_stream(raw)
        table = reader.read_all()
        success, result = endpoint.compute(payload=table)
        if success:
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, result.schema) as writer:
                writer.write(result)
            ipc_bytes = sink.getvalue().to_pybytes()
            return Response(
                content = ipc_bytes,
                status_code = status.HTTP_200_OK,
                media_type= "application/vnd.apache.arrow.stream"
            )
        return Response(
            content = result.column("error_message")[0].as_py(),
            status_code = status.HTTP_400_BAD_REQUEST,
            media_type= "application/vnd.apache.arrow.stream"
        )
    except (ValueError, KeyError) as e:
        return Response(
            content = f"{type(e).__name__}: {str(e)}",
            status_code = status.HTTP_400_BAD_REQUEST,
            media_type= "application/vnd.apache.arrow.stream"
        )
