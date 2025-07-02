import json
from pyomo.environ import *
from service.optimization_service.ampl_expression.ampl_interpreter import build_model_structure, attach_constraints_and_objective

def run():
    
    # ---- Build model based on IR ----
    print("Starting AMPL Expression")
    # ---- Load JSON IR ----
    with open("solvers\\ampl_expression\\sample.json") as f:
        model_ir = json.load(f)

    # ---- Create Pyomo Model ----
    model = build_model_structure(model_ir)

    # ---- Populate Data (stub for now) ----
    # In practice, load real data from JSON or .dat file
    # Sample data
    foods = ["bread", "milk"]
    nutrients = ["calories", "protein"]
    model.FOODS = foods
    model.NUTRIENTS = nutrients
    model.cost["bread"] = 1.0
    model.cost["milk"] = 2.0

    model.n_min["calories"] = 2000
    model.n_max["calories"] = 3000
    model.n_min["protein"] = 50
    model.n_max["protein"] = 100

    model.amt["calories", "bread"] = 100
    model.amt["calories", "milk"] = 150
    model.amt["protein", "bread"] = 4

    attach_constraints_and_objective(model, model_ir)
    
    # ---- Solve (Optional) ----
    solver = SolverFactory("glpk")
    result = solver.solve(model)

    # ---- Display results ----
    print("Objective:", value(model.obj))
    for f in model.FOODS:
        print(f"Buy[{f}] = {value(model.Buy[f])}")
        
