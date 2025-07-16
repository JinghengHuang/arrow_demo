
import time
import json
import pytest
import pyarrow as pa
import requests
from src.utils.dict_to_pa_table import dict_to_pa_table
import src.utils.network_check as ncheck
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random


with open("tests/ipc_http_test/qp.json", "r", encoding='utf-8') as f:
    data = json.load(f)
    model_data = data["model_data"]  # turn model_data json into a dictionary
    solvers = data["solvers"]


@pytest.mark.parametrize("solver", solvers)
def test_julia_flow(solver):
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/compute"

    ipc_dict = {
        "model" :model_data,
        "model_name": "test_qp",
        "engine": "julia",
        "solver": solver
    }
    ipc_table = dict_to_pa_table(ipc_dict)

    # convert to ipc stream
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
        writer.write(ipc_table)

    # converts to bytes
    ipc_bytes = sink.getvalue().to_pybytes()

    # set headers for the request
    headers = {
        "Content-Type": "application/vnd.apache.arrow.stream"
    }

    pre = time.time()
    # send the request
    response = requests.post(url, data=ipc_bytes, headers=headers)

    # check the response
    print(response.status_code)
    print(response.content)
    
    post = time.time()
    diff = post - pre
    print(f"Pre request: {pre}")
    print(f"Post request: {post}")
    print(f"Time diff: {diff}")

# test_julia_flow()

# # send 50 requests in parallel
# async def main():
#     loop = asyncio.get_event_loop()

#     with ThreadPoolExecutor(max_workers=10) as executor: 
#         tasks = [
#             loop.run_in_executor(executor, test_julia_flow)
#             for i in range(50) 
#         ]
#         await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     asyncio.run(main())
