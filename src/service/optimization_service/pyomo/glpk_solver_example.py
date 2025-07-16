import pyomo.environ as pyo
import pyarrow as pa
from service.optimization_service.solver import BaseSolver

# Example solver taken from pyomo tutorial implementing base solver
class GlpkSolverSample(BaseSolver):
    def __init__(self):
        super().__init__()
        self.A = ['hammer', 'wrench', 'screwdriver', 'towel']
        self.b = {'hammer':8, 'wrench':3, 'screwdriver':6, 'towel':11}
        self.w = {'hammer':5, 'wrench':7, 'screwdriver':4, 'towel':3}
        self.W_max = 14
    
    # Run the solver from dict
    def run(self, params:dict) -> dict:
        A = params["A"]
        b = params["b"]
        w = params["w"]
        W_max = params["W_max"]
    
        return self.glpk_example(A, b, w, W_max)
    
    # Run the solver
    def run(self, params:pa.Table) -> pa.Table:
        params_content = params.to_pydict()
        A = params_content["A"]
        b = params_content["b"]
        w = params_content["w"]
        W_max = params_content["W_max"][0]
        
        exec_result = self.glpk_example(A, b, w, W_max)        
        result = pa.table(
            [exec_result.get("output_keys"), exec_result.get("output_values")],
            names=["Item", "Value"]
        )
        
        return result
    
    def glpk_example(self, A, b, w, W_max) -> dict:
        if A is None or b is None or w is None or W_max is None:
            raise ValueError("Parameter value missing!")
        model = pyo.ConcreteModel()
        model.x = pyo.Var( range(0, len(A)), within=pyo.Binary )

        model.obj = pyo.Objective(
            expr = sum( b[i]*model.x[i] for i in range(0, len(A)) ), 
            sense = pyo.maximize )

        model.weight_con = pyo.Constraint(
            expr = sum( w[i]*model.x[i] for i in range(0, len(A)) ) <= W_max )

        opt = pyo.SolverFactory('glpk')
        opt_success = opt.solve(model)

        total_weight = sum( w[i]*pyo.value(model.x[i]) for i in range(0, len(A)) )
        
        output_keys = []
        output_values = []
        output_keys.append("Total Weight")
        output_values.append(str(total_weight))
        output_keys.append("Total Benefit")
        output_values.append(str(pyo.value(model.obj)))
    
        for i in range(0, len(A)):
            acquired = 'No'
            if pyo.value(model.x[i]) >= 0.5:
                acquired = 'Yes'
            output_keys.append(A[i])
            output_values.append(acquired)
        return {
            "output_keys": output_keys,
            "output_values": output_values,
        }
