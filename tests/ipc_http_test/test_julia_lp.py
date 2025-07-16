import time
import json
import pytest
import requests
import pyarrow as pa
from utils.dict_to_pa_table import dict_to_pa_table
import utils.network_check as ncheck


# read data from lp.json
with open("tests/ipc_http_test/lp.json", "r", encoding='utf-8') as f:
    data = json.load(f)
    model_data = data["model_data"] # turn model_data json into a dictionary
    solvers = data["solvers"]   


@pytest.mark.parametrize("solver", solvers)
def test_julia_flow(solver):
    if ncheck.check_socket("127.0.0.1", 8000) is False:
        pytest.skip("Server is not started")
    url = "http://127.0.0.1:8000/compute"

    ipc_dict = {
        "model" : model_data,
        "model_name": "test_lp",
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
    print(response.content)
    # assert response.status_code == 200, f"Request failed with status code {response.status_code}"

    post = time.time()
    diff = post - pre
    print(f"Pre request: {pre}")
    print(f"Post request: {post}")
    print(f"Time diff: {diff}")

# for solver in solvers:
#     # if solver["solver_name"] == "HiGHS":
#         test_julia_flow(solver)  # Run the test for each solver
#         sleep(3)  # Optional: sleep to avoid overwhelming the server with requests
