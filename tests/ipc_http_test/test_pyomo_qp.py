
import pyarrow as pa
import pyarrow.ipc as ipc
import requests
import time
from service.optimization_service.pyomo.cobra_qp_solver import CobraQPSolver
from utils.dict_to_pa_table import dict_to_pa_table
# Use Server to test:

# Quadratic term Q as native Python dict
Q = { 
    "row": [0, 1],
    "col": [0, 1],
    "val": [2.0, 2.0]
}

# Linear term c
c = [1.0, 1.0]

# Equality constraint A = b
A = {
    "row": [0, 0],
    "col": [0, 1],
    "val": [1.0, 1.0]
}
b = [1.0]

# Inequality constraint Gx <= h
G = {
    "row": [0, 1],
    "col": [0, 1],
    "val": [-1.0, -1.0]
}
h = [0.0, 0.0]

# Variable bounds
lb = [0.0, 0.0]
ub = [10.0, 10.0]

# Objective sense
osense = "min"


model_name ="test_qp"
engine = "pyomo"
solver_name = "HiGHS"
solver_type = "QP"
solver_params = {"presolve": True, "dual": True, "primal": True}

model = {
        "Q":Q,
        "c": c,
        "A": A,
        "b": b,
        "G": G,
        "h": h,
        "lb": lb,
        "ub": ub,
        "osense": osense}
    
# def test_pyomo():
#     url = "http://127.0.0.1:8000/compute"

    
#     model_name ="test_qp"
#     engine = "pyomo"
#     solver_name = "HiGHS"
#     solver_type = "QP"
#     solver_params = {"presolve": True, "dual": True, "primal": True}
    
#     ipc_dict = {
#         "model" :model,
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

#     pre = time.time()
#     # send the request
#     response = requests.post(url, data=ipc_bytes, headers=headers)
#     assert "Error" not in str(response.content)
#     print(str(response.content))
#     post = time.time()
#     diff = post - pre
#     print(f"Pre request: {pre}")
#     print(f"Post request: {post}")
#     print(f"Time diff: {diff}")

# No server
def test_pyomo_qp_highs():
    
    # Stress test
    model["solver"] = {
        "solver_name": "HiGHS",
        "solver_type": "QP",
        # some params not supported on QP, see https://ergo-code.github.io/HiGHS/dev/options/definitions/#option-definitions for lists of supported params
        "solver_params": {"presolve": "on", "time_limit": 10, "parallel": "on"}
    }
    solver = CobraQPSolver()
    result = solver.run(model)
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    assert "error" not in str(result)
    print(result)

# Glpk doesn't support qp, so no test for this
# def test_pyomo_qp_glpk():
    
#     # Stress test
#     model["solver"] = {
#         "solver_name": "glpk",
#         "solver_type": "QP",
#         "solver_params": {"presolve": True, "dual": True, "primal": True}
#     }
#     solver = CobraQPSolver()
#     result = solver.run(model)
#     assert "Exception" not in str(result)
#     assert "Error" not in str(result)
#     print(result)

def test_pyomo_qp_gurobi():
    
    # Stress test
    model["solver"] = {
        "solver_name": "gurobi",
        "solver_type": "QP",
        "solver_params": {"presolve": True, "quad": 1}
    }
    solver = CobraQPSolver()
    result = solver.run(model)
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    print(result)

# Maybe cplex in the future, but not now.
# def test_pyomo_qp_cplex():
    
#     # Stress test
#     model["solver"] = {
#         "solver_name": "cplex",
#         "solver_type": "QP",
#         "solver_params": {"presolve": True, "dual": True, "primal": True}
#     }
#     solver = CobraQPSolver()
#     result = solver.run(model)
#     assert "Exception" not in str(result)
#     assert "Error" not in str(result)
#     print(result)

def test_pyomo_qp_ipopt():
    
    # Stress test
    model["solver"] = {
        "solver_name": "ipopt",
        "solver_type": "QP",
    }
    solver = CobraQPSolver()
    result = solver.run(model)
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    print(result)