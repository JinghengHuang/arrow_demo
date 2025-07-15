import pyarrow.compute as pc
import numpy as np

class SolverConfig:
    def __init__(self, name, handle=None):
        self.name = name.upper()
        self.handle = handle

def change_cobra_solver(name: str, params=None, print_level=1) -> SolverConfig:
    name = name.upper()
    # Not managing this in the code, let pyomo decide and raise exception if not supported
    # known_solvers = ["GLPK", "CPLEX", "GUROBI", "HIGHS", "APPSI_HIGHS", "IPOPT"]
    # if name not in known_solvers:
    #     raise ValueError(f"Unsupported solver: {name}")
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