"""
    LPproblem(S, b, c, lb, ub, osense, csense, rxns, mets)

General type for storing an LP problem which contains the following fields:

- `S`:              LHS matrix (m x n)
- `b`:              RHS vector (m x 1)
- `c`:              Objective coefficient vector (n x 1)
- `lb`:             Lower bound vector (n x 1)
- `ub`:             Upper bound vector (n x 1)
- `osense`:         Objective sense (scalar; -1 ~ "max", +1 ~ "min")
- `csense`:         Constraint senses (m x 1, 'E' or '=', 'G' or '>', 'L' ~ '<')
- `solver`:         A `::SolverConfig` object that contains a valid `handle` to the solver

"""
import pyomo.environ as pyo
import pyarrow as pa
from service.optimization_service.solver import BaseSolver

class CobraLP(BaseSolver):
    def __init__(self):
        self.model = {}
        super().__init__()
        
        
    def run(self, params:dict) -> dict:
        # Convert the data into an model acceptable format
        for k, v in params.items():
            self.model[k] = v
        
        # Send the data to model
        # Get results, for now just use glpk
        return self.solve_cobra_lp(self.model, {"solverName": "glpk"})

    def solve_cobra_lp(self, model, solver):
        model_dict = self.buildCobraLP(model, solver)
        resdict = self.solvelp(model_dict.model, model_dict.x)

        if resdict.status == "Optimal":
            resdict.objval = model.osense * resdict.objval
        return resdict
    
    def buildCobraLP(self, model, solver):
        if solver.handle != -1:
            # prepare the csense vector when letters instead of symbols are used
            for i in range(len(model.csense)):
                if model.csense[i] == 'E':
                    model.csense[i] = '='
                if model.csense[i] == 'G':
                    model.csense[i] = '>'
                if model.csense[i] == 'L':
                    model.csense[i] = '<'
            return self.buildlp(model.osense * model.c, model.S, model.csense, model.b, model.lb, model.ub, solver.handle)
        else:
            raise ValueError("The solver is not supported. Please set solver name to one the supported solvers.")
    
    
    def solvelp(self, opt, model, x):
        result = opt.solve(model)
        return result
        
    def buildlp(self, c, A, sense, b, l, u, solver):
        N = len(c)
        opt = pyo.SolverFactory(solver["solverName"])
        model = pyo.ConcreteModel()
        model.x = pyo.Var( range(1, N), bounds=(l, u) )

        model.obj = pyo.Objective(
            expr = min( c * model.x ), 
            sense = pyo.maximize )
        eq_rows = sense == '='
        ge_rows = sense == '>'
        le_rows = sense == '<'
        model.con_1 = pyo.Constraint( expr = A[eq_rows] * model.x = b[eq_rows])
        model.con_2 = pyo.Constraint( expr = A[ge_rows] * model.x = b[ge_rows])
        model.con_3 = pyo.Constraint( expr = A[le_rows] * model.x = b[le_rows])

        return {
            "opt": opt, 
            "model":model, 
            "x": model.x, 
            "c": c
        }