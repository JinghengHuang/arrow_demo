"""
QPModel: Quadratic Programming Model Representation using PyArrow
"""

import pyarrow as pa
from src.objects.base_model import ArrowModel
from src.utils.model_sanity_check import check_arrow_coo_matrix, check_variable_bounds, check_objective_sense


class QPModel(ArrowModel):
    """
    QPModel: Quadratic Programming Model Representation using PyArrow

    Standard QP form:
        minimize     1/2 xᵀ Q x + cᵀ x
        subject to   A x = b            (equality constraints)
                    G x <= h           (inequality constraints)
                    lb <= x <= ub      (bounds)

    Components:
        - Q: Quadratic coefficient matrix (symmetric, sparse COO format)
        - c: Linear coefficient vector
        - A, b: Equality constraint matrix and RHS
        - G, h: Inequality constraint matrix and RHS(optional)
        - lb, ub: Variable bounds(optional)
        - osense: Objective sense, e.g., "min" or "max"(optional, defaults to "min")
    
    All components are stored using PyArrow for efficient in-memory processing
    and IPC serialization.
    """

    def __init__(self, model_dict: dict):
        """
        Initialize QP model.

        Required:
            - Q (RecordBatch): Sparse quadratic coefficient matrix in COO format with "row", "col", "val"
            - c (Array): Linear coefficients
            - A (RecordBatch): Sparse equality constraint matrix in COO format with "row", "col", "val"
            - b (Array): Right-hand side vector for equality constraints
        Optional:
            - G (RecordBatch): Sparse inequality constraint matrix in COO format with "row", "col", "val"
            - h (Array): Right-hand side vector for inequality constraints
            - lb (Array): Lower bounds for variables (default: None, treated as unbounded)
            - ub (Array): Upper bounds for variables (default: None, treated as unbounded)
            - osense (Scalar): "min" or "max" (default: "min
        """
        Q = pa.RecordBatch.from_pydict(model_dict.get("Q"))
        c = model_dict.get("c")
        A = pa.RecordBatch.from_pydict(model_dict.get("A"))
        b = model_dict.get("b")
        G = pa.RecordBatch.from_pydict(model_dict.get("G", None))
        h = model_dict.get("h", None)
        lb = model_dict.get("lb", None)
        ub = model_dict.get("ub", None)
        osense = pa.scalar(model_dict.get("osense", "min"), type=pa.string())
        
        for name, mat in [("Q", Q), ("A", A)] + ([("G", G)] if G is not None else []):
            if not isinstance(mat, pa.RecordBatch):
                raise TypeError(f"{name} must be a pyarrow.RecordBatch")
            if not all(col in mat.schema.names for col in ["row", "col", "val"]):
                raise ValueError(f"{name} must contain columns 'row', 'col', 'val'")

        self.Q = Q
        self.c = c
        self.A = A
        self.b = b
        self.G = G
        self.h = h
        self.lb = lb
        self.ub = ub
        self.osense = osense if osense is not None else pa.scalar("min", type=pa.string())


    def sanity_check(self):
        """
        Sanity checks for QP model consistency.

        - Q matrix should not reference out-of-bound variables
        - A, G matrices' row/col should be in valid range
        - Vector dimensions must match (c, b, h, lb, ub)
        - osense must be "min" or "max"
        """
        n_vars = len(self.c)
        n_eqs = len(self.b)
        n_ineqs = len(self.h) if self.h is not None else 0

        check_arrow_coo_matrix("Q", self.Q, n_vars, n_vars)
        check_arrow_coo_matrix("A", self.A, n_eqs, n_vars)
        if self.G is not None:
            check_arrow_coo_matrix("G", self.G, n_ineqs, n_vars)       

        # Bounds
        check_variable_bounds(self.lb, self.ub, n_vars)

        # osense
        check_objective_sense(self.osense)
