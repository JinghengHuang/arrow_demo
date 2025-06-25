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
        # Get results
        return self.model