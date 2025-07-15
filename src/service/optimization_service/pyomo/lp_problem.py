from pyomo.environ import *
import numpy as np
from pyomo.opt import SolverStatus, TerminationCondition
import pyarrow.compute as pc
import os
import gc
from utils.pyomo_utils import *

class LPProblem:
    def __init__(self, S, b, c, lb, ub, osense, csense):
        if isinstance(S, dict) and all(k in S for k in ("row", "col", "val")):
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
            expr = sum(self.S[j, i] * model.x[i] for i in range(self.S.shape[1]))
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

    def solve(self, solver_params=None):
        if self.model is None or self.solver is None:
            raise RuntimeError("Model not built or solver not assigned.")
        opt = SolverFactory(self.solver.name.lower())
        if solver_params is not None:
            result = opt.solve(self.model, tee=False, solver_options=solver_params)
        else:
            result = opt.solve(self.model, tee=False)

        self.status = str(result.solver.termination_condition)
        if result.solver.termination_condition == TerminationCondition.optimal:
            print("Solved.")
            self.solution = [value(self.model.x[i]) for i in self.model.I]
            self.objective_value = value(self.model.obj)
            if self.osense == 1:
                self.objective_value = -self.objective_value
        else:
            self.solution = "Infeasible"
            self.objective_value = None
            self.solution = None
