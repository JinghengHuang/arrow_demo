from typing import Union, Annotated
import pyarrow as pa
import pyarrow.ipc as ipc
from fastapi import Request
import io
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from controller.endpoints import *

app = FastAPI()
endpoint = Endpoint()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/compute")
async def compute(request: Request):
    raw = await request.body()
    reader = pa.ipc.open_stream(raw)
    table = reader.read_all()
    result = endpoint.compute(payload=table)
    result = result.to_pydict()
    return {
        "message": f"Computing model successful",
        "result": result
    }

@app.post("/saveModel")
async def save(model_id: Annotated[Optional[str], Form()] = None, 
            model_name: Annotated[Optional[str], Form()] = None, 
            model: Annotated[UploadFile, File(), None] = None):
    """
        Save a model to the server.
        :param model_id: Optional model ID
        :param model_name: Name of the model, if not provided can use ID extracted from the model file
        :param model: The model file to save, expected to be in .mat format
        :return: A message indicating success or failure
    """
    contents = await model.read()
    mat_dict = endpoint.parse_model(contents)
    mat_model = mat_dict['engine_model']
    ipc_dict = mat_model.to_ipc_bytes()
    # handle model saving logic
    endpoint.save_model(payload={
        "model_id": model_id,
        "model_name": model_name,
        "model": contents
    })
    return {"message": f"Saving model {model_name} successful, file size: {len(contents)}"}