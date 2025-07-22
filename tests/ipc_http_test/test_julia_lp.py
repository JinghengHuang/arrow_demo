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

    post = time.time()
    diff = post - pre
    print(f"Pre request: {pre}")
    print(f"Post request: {post}")
    print(f"Time diff: {diff}")

    # assert , if solver is Gurobi and Mosek, the response should be 500 due to missing license
    if solver["solver_name"] in ["Gurobi", "MOSEK"]:
        assert response.status_code == 500, f"Request failed with status code {response.status_code}"
    else:
        assert response.status_code == 200, f"Request failed with status code {response.status_code}"
        # check if the response is a valid ipc stream
        reader = pa.ipc.open_stream(response.content)
        result_table = reader.read_all()
        assert result_table.num_rows > 0, "Result table is empty"
        assert "solution" in result_table.column_names, "Solution column not found in result table"
        assert "objective_value" in result_table.column_names, "Objective value column not found in result table"
        solution = result_table.column("solution")[0].as_py()
        objective_value = result_table.column("objective_value")[0].as_py()
        assert solution is not None, "Solution is None"
        assert objective_value is not None, "Objective value is None"
        # check the number of variables in the solution matches the number of variables in the model
        assert len(solution) == len(model_data["c"]), "Number of variables in solution does not match number of variables in model"
