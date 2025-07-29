
import time
import json
import pytest
import pyarrow as pa
import requests
from utils.dict_to_pa_table import dict_to_pa_table
import utils.network_check as ncheck
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

    # assert , if solver is Gurobi and Mosek, the response should be 500 due to missing license
    if solver["solver_name"] in ["Gurobi", "MOSEK"]:
        assert response.status_code == 500, f"Request failed with status code {response.status_code}"
        assert "license" in response.text.lower(), "License error message not found in response"
    elif solver["solver_name"] == "GLPK":
        assert response.status_code == 500, f"Request failed with status code {response.status_code}"
        assert "MathOptInterface.UnsupportedAttribute" in response.text, "GLPK error message not found in response"
    elif solver["solver_name"] == "HiGHS" and solver["solver_params"].get("presolve", 0) != 0:
        assert response.status_code == 500, f"Request failed with status code {response.status_code}"
        assert "Invalid value" in response.text
    else:
        assert response.status_code == 200, f"Request failed with status code {response.status_code}"
        # check if the response is a valid ipc stream
        reader = pa.ipc.open_stream(response.content)
        result_table = reader.read_all()
        assert isinstance(result_table, pa.Table), "Response is not a valid IPC stream"
        assert "solution" in result_table.column_names, "Response does not contain 'solution' column"
        assert result_table.num_rows > 0, "Response table is empty"
        print(f"Test passed for solver: {solver['solver_name']}")
        # check the number of variables in the solution matches the number of variables in the model
        solution = result_table.column("solution")[0].as_py()
        objective_value = result_table.column("obj_val")[0].as_py()
        print(solution, objective_value)
        assert solution is not None, "Solution is None"
        assert objective_value is not None, "Objective value is None"
        assert len(solution) == len(model_data["c"]), "Number of variables in solution does not match number of variables in model"