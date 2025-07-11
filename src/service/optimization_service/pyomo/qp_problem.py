from pyomo.environ import *
import numpy as np
from pyomo.opt import SolverStatus, TerminationCondition
import pyarrow.compute as pc
from gethighs import HiGHS
import os
import gc

class SolverConfig:
    def __init__(self, name, handle=None):
        self.name = name.upper()
        self.handle = handle

class QPProblem:
    def __init__(self, A, G, Q, b, c, h, lb, osense, ub):
        if isinstance(A, dict) and all(k in A for k in ("row", "col", "val")):
            # Convert to dense
            self.A = sparse_dict_to_dense(A)
        else:
            # If it's dense already
            self.A = np.array(A)

        if isinstance(G, dict) and all(k in G for k in ("row", "col", "val")):
            # Convert to dense
            self.G = sparse_dict_to_dense(G)
        else:
            # If it's dense already
            self.G = np.array(G)
        if isinstance(Q, dict) and all(k in Q for k in ("row", "col", "val")):
            # Convert to dense
            self.Q = sparse_dict_to_dense(Q)
        else:
            # If it's dense already
            self.Q = np.array(Q)
        self.b = np.array(b)
        self.c = np.array(c)
        self.h = np.array(h)
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.n = self.c.shape[0]
        self.meq = self.A.shape[0]
        self.mieq = self.G.shape[0]
        if osense == 'max':
            self.osense = 1
        elif osense == 'min':
            self.osense = -1
        self.model = None
        self.solution = None
        self.objective_value = None
        self.status = None

    def build_qp(self, solver: SolverConfig):
        model = ConcreteModel()
                
        n = self.c.shape[0]
        model.I = RangeSet(0, n - 1)

        print("Setting x:")
        model.x = Var(model.I, within=Reals)

        # Bounds
        for i in model.I:
            model.x[i].setlb(self.lb[i])
            model.x[i].setub(self.ub[i])

        print("Setting objectives:")
        # Objective
        def objective_rule(m):
            quad = sum(self.Q[i, j] * m.x[i] * m.x[j] for i in m.I for j in m.I)
            linear = sum(self.c[i] * m.x[i] for i in m.I)
            return 0.5 * quad + linear

        model.obj = Objective(rule=objective_rule, sense=minimize if self.osense == -1 else maximize)

        # S is now always dense 2D array
        # Setting constraints
        print("Setting constraints:")
        def eq_constraint_rule(m, i):
            return sum(self.A[i, j] * m.x[j] for j in m.I) == self.b[i]

        model.E = RangeSet(0, self.meq - 1)
        model.eq_constraints = Constraint(model.E, rule=eq_constraint_rule)
        
        
        def ineq_constraint_rule(m, i):
            return sum(self.G[i, j] * m.x[j] for j in m.I) <= self.h[i]

        model.INEQ = RangeSet(0, self.mieq - 1)
        model.ineq_constraints = Constraint(model.INEQ, rule=ineq_constraint_rule)
        self.model = model
        self.solver = solver

    def solve(self):
        if self.model is None or self.solver is None:
            raise RuntimeError("Model not built or solver not assigned.")
        sol_path = "./sol.sol"
        if "highs" in self.solver.name.lower(): 
            opt = HiGHS(solution_file=sol_path, mip_heuristic_effort=0.2, mip_detect_symmetry="on")
        elif "gurobi" in self.solver.name.lower():
            opt = SolverFactory(self.solver.name.lower(), solver_io="python")
        else:
            opt = SolverFactory(self.solver.name.lower())

        result = opt.solve(self.model)
        if "highs" in self.solver.name.lower(): 
            self.status = str(opt.status)
            print(opt)
            if self.status == "Optimal":
                # Get from the sol file
                x = []
                with open(sol_path, "r") as f:
                    lines = f.readlines()
                    section = None
                    is_primal = False
                    for j, line in enumerate(lines):
                        if "# Primal solution values" in line:
                            is_primal = True
                            continue
                        if "Columns" in line:
                            section = "col"
                            continue
                        if "Rows" in line:
                            section = "row"
                            continue
                        if "Dual solution values" in line:
                            is_primal = False
                            continue
                        if is_primal and section == "col":
                            parts = line.strip().split()
                            val = float(parts[-1])
                            x.append(val)
                        
                
                if os.path.exists(sol_path):
                    os.remove(sol_path)
                self.solution = [x]
                self.objective_value = value(opt.objective)
                if self.osense == 1:
                    self.objective_value = -self.objective_value
            else:
                self.solution = self.status
                self.objective_value = None
        else:

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
    known_solvers = ["GLPK", "CPLEX", "GUROBI", "HIGHS", "APPSI_HIGHS", "IPOPT"]
    if name not in known_solvers:
        raise ValueError(f"Unsupported solver: {name}")
    return SolverConfig(name)


def sparse_dict_to_dense(S_dict, shape=None):
    row = S_dict["row"]
    col = S_dict["col"]
    data = S_dict["val"]
    if shape is None:
        n_row = int(pc.max(row).as_py()) + 1 if row else 0
        n_col = int(pc.max(col).as_py()) + 1 if col else 0
        shape = (n_row, n_col)
    dense = np.zeros(shape)
    for r, c, v in zip(row, col, data):
        dense[r, c] = v
    return dense