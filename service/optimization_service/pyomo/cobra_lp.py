from pyomo.environ import *
import numpy as np
from collections import defaultdict
import pyarrow.compute as pc


class SolverConfig:
    def __init__(self, name, handle=None):
        self.name = name.upper()
        self.handle = handle


class LPProblem:
    def __init__(self, S, b, c, lb, ub, osense, csense):
        if isinstance(S, dict) and all(k in S for k in ("row", "col", "data")):
            # 处理稀疏字典格式，直接保存
            self.S = sparse_dict_to_dense(S)
        else:
            # 假设是可转换为 NumPy 数组的稠密矩阵
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
        num_vars = len(self.c)
        num_cons = len(self.b)

        model = ConcreteModel()
        model.I = RangeSet(0, num_vars - 1)
        model.J = RangeSet(0, num_cons - 1)

        model.x = Var(model.I, domain=Reals)

        # Bounds
        for i in model.I:
            model.x[i].setlb(self.lb[i])
            model.x[i].setub(self.ub[i])

        # Objective
        if self.osense == -1:
            model.obj = Objective(expr=sum(self.c[i] * model.x[i] for i in model.I), sense=maximize)
        else:
            model.obj = Objective(expr=sum(self.c[i] * model.x[i] for i in model.I), sense=minimize)

        # Constraints
        model.constraints = ConstraintList()
        # S is now always dense 2D array
        for j in range(num_cons):
            expr = sum(self.S[j][i] * model.x[i] for i in range(num_vars))
            sense = self.csense[j]
            if sense in ['=', 'E']:
                model.constraints.add(expr == self.b[j])
            elif sense in ['<', 'L']:
                model.constraints.add(expr <= self.b[j])
            elif sense in ['>', 'G']:
                model.constraints.add(expr >= self.b[j])
            else:
                raise ValueError(f"Invalid constraint sense: {sense}")

        self.model = model
        self.solver = solver

    def solve(self):
        if self.model is None or self.solver is None:
            raise RuntimeError("Model not built or solver not assigned.")

        opt = SolverFactory(self.solver.name.lower())
        result = opt.solve(self.model, tee=False)

        self.status = str(result.solver.termination_condition)
        if self.status.lower() == "optimal":
            self.solution = [value(self.model.x[i]) for i in self.model.I]
            self.objective_value = value(self.model.obj)
            if self.osense == -1:
                self.objective_value = -self.objective_value
        else:
            self.solution = None
            self.objective_value = None


def change_cobra_solver(name: str, params=None, print_level=1) -> SolverConfig:
    name = name.upper()
    known_solvers = ["GLPK", "CPLEX", "GUROBI", "HIGHS"]
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