from pyomo.environ import *
import numpy as np
from pyomo.opt import SolverStatus, TerminationCondition
import pyarrow.compute as pc
import os
import gc

class SolverConfig:
    def __init__(self, name, handle=None):
        self.name = name.upper()
        self.handle = handle


class LPProblem:
    def __init__(self, S, b, c, lb, ub, osense, csense):
        if isinstance(S, dict) and all(k in S for k in ("row", "col", "data")):
            # Convert to dense
            self.S = sparse_dict_to_dense(S)
        else:
            # If it's dense already
            self.S = np.array(S)
        self.n_mets, self.n_rxns = self.S.shape

        self.b = np.array(b)
        self.c = np.array(c)
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        if osense == 'max':
            self.osense = 1
        elif osense == 'min':
            self.osense = -1
        self.csense = np.array(csense)
        self.model = None
        self.solution = None
        self.objective_value = None
        self.status = None

    def build_lp(self, solver: SolverConfig):
        model = ConcreteModel()
                
        n = self.c.shape[0]
        m = self.b.shape[0]
        model.I = RangeSet(0, n - 1)
        model.J = RangeSet(0, m - 1)

        print("Setting x:")
        model.x = Var(model.I, domain=Reals)

        # Bounds
        for i in model.I:
            model.x[i].setlb(self.lb[i])
            model.x[i].setub(self.ub[i])

        print("Setting objectives:")
        # Objective
        model.obj = Objective(expr=sum(self.c[i] * model.x[i] for i in model.I), sense=minimize if self.osense == -1 else maximize)

        # S is now always dense 2D array
        # Setting constraints
        print("Setting constraints:")
        i = 0
        j = 0
        model.constraints = ConstraintList()
        
        for j in range(self.S.shape[0]):
            print(f"Setting expression for {j}:")
            expr = sum(self.S[j, i] * model.x[i] for i in range(self.S.shape[1]))
            print(f"Setting expression for {j} done")
            if self.csense[j] in ['E', '=']:
                model.constraints.add(expr == self.b[j])
            elif self.csense[j] in ['L', '<']:
                model.constraints.add(expr <= self.b[j])
            elif self.csense[j] in ['G', '>']:
                model.constraints.add(expr >= self.b[j])
            else:
                raise ValueError(f"Invalid constraint sense: {self.csense[j]}")
        self.model = model
        self.solver = solver

    def solve(self):
        if self.model is None or self.solver is None:
            raise RuntimeError("Model not built or solver not assigned.")

        opt = SolverFactory(self.solver.name.lower())
        result = opt.solve(self.model, tee=False)

        self.status = str(result.solver.termination_condition)
        if (result.solver.status == SolverStatus.ok) and (result.solver.termination_condition == TerminationCondition.optimal):
            print("Solved.")
            self.solution = [value(self.model.x[i]) for i in self.model.I]
            self.objective_value = value(self.model.obj)
            if self.osense == 1:
                self.objective_value = -self.objective_value
        elif result.solver.termination_condition == TerminationCondition.infeasible:
            self.solution = "Infeasible"
            self.objective_value = None


def change_cobra_solver(name: str, params=None, print_level=1) -> SolverConfig:
    name = name.upper()
    known_solvers = ["GLPK", "CPLEX", "GUROBI", "HIGHS", "APPSI_HIGHS"]
    if name not in known_solvers:
        raise ValueError(f"Unsupported solver: {name}")
    return SolverConfig(name)


def sparse_dict_to_dense(S_dict, shape=None):
    row = S_dict["row"]
    col = S_dict["col"]
    data = S_dict["data"]
    if shape is None:
        n_row = int(pc.max(row).as_py()) + 1 if row else 0
        n_col = int(pc.max(col).as_py()) + 1 if col else 0
        shape = (n_row, n_col)
    dense = np.zeros(shape)
    for r, c, v in zip(row, col, data):
        dense[r, c] = v
    return dense