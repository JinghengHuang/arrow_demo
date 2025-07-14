# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

import requests,time
import pyarrow as pa
from utils.dict_to_pa_table import dict_to_pa_table
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random

# def test_julia_flow():
#     url = "http://127.0.0.1:8000/compute"
    
#     # Quadratic term Q as native Python dict
#     Q = { 
#         "row": [0, 1],
#         "col": [0, 1],
#         "val": [2.0, 2.0]
#     }

#     # Linear term c
#     c = [1.0, 1.0]

#     # Equality constraint A = b
#     A = {
#         "row": [0, 0],
#         "col": [0, 1],
#         "val": [1.0, 1.0]
#     }
#     b = [1.0]

#     # Inequality constraint Gx <= h
#     G = {
#         "row": [0, 1],
#         "col": [0, 1],
#         "val": [-1.0, -1.0]
#     }
#     h = [0.0, 0.0]

#     # Variable bounds
#     lb = [0.0, 0.0]
#     ub = [10.0, 10.0]

#     # Objective sense
#     osense = "min"

    
    # model_name ="test_qp"
    # engine = "julia"
    # solver_name = "HiGHS"  # Example solver name
    # # solver_name = "GLPK"  # Example solver name
    # solver_type = "QP" 
    # solver_params = {"presolve": "on","kkt_tolerance": 1e-6}  # Example solver parameters
    
#     ipc_dict = {
#         "model" :{
#         "Q":Q,
#         "c": c,
#         "A": A,
#         "b": b,
#         "G": G,
#         "h": h,
#         "lb": lb,
#         "ub": ub,
#         "osense": osense},
#         "model_name": model_name,
#         "engine": engine,
#         "solver": {
#             "solver_name": solver_name,
#             "solver_type": solver_type,
#             "solver_params": solver_params
#         }
#     }
#     ipc_table = dict_to_pa_table(ipc_dict)
    
#     # convert to ipc stream
#     sink = pa.BufferOutputStream()
#     with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
#         writer.write(ipc_table)
        
    
#     # converts to bytes
#     ipc_bytes = sink.getvalue().to_pybytes()

#     # set headers for the request
#     headers = {
#         "Content-Type": "application/vnd.apache.arrow.stream"
#     }

    # pre = time.time()
#     # send the request
#     response = requests.post(url, data=ipc_bytes, headers=headers)

#     # check the response
#     print(response.status_code)
#     print(response.content)
    
    # post = time.time()
    # diff = post - pre
    # print(f"Pre request: {pre}")
    # print(f"Post request: {post}")
    # print(f"Time diff: {diff}")

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
