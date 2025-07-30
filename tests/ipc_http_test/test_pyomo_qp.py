from service.optimization_service.python.pyomo.cobra_qp_solver import CobraQPSolver
import pytest
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

solvers = [
    pytest.param({"solver_name": "Gurobi", "solver_type": "QP", "solver_params": {}}, id="Gurobi"),
    pytest.param({"solver_name": "HiGHS", "solver_type": "QP", "solver_params": {}}, id="HiGHS"),
    pytest.param({"solver_name": "HiGHS", "solver_type": "QP", "solver_params": {"presolve": 1}}, id="HiGHS w/params"),
    pytest.param({"solver_name": "Ipopt", "solver_type": "QP", "solver_params": {}}, id="Ipopt")
    # {"solver_name": "Hypatia", "solver_type": "QP", "solver_params": {}}
]
# No server
@pytest.mark.parametrize("solver", solvers)
def test_pyomo_qp_no_server(solver):
    model["solver"] = solver
    solver = CobraQPSolver()
    result = solver.run(model)
    assert True == result.get("success")
    assert "Exception" not in str(result)
    assert "Error" not in str(result)
    print(result)
