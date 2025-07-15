import pyarrow as pa
import pyarrow.compute as pc
from .base_model import ArrowModel
from utils.model_sanity_check import check_arrow_coo_matrix, check_variable_bounds, check_objective_sense

"""
LPModel: Linear Programming Model Representation using PyArrow

This class provides a structured way to represent a standard linear programming (LP) model
using Arrow's in-memory format for high-performance serialization and communication.

Standard LP form:
    minimize     c^T x
    subject to   A x = b
                 lb <= x <= ub

Model Components:
    - A:       Constraint matrix in sparse COO format (as a RecordBatch with columns "row", "col", "val")
    - b:       Right-hand side vector
    - c:       Objective function coefficients
    - lb:      Lower bound for each variable(Optional)
    - ub:      Upper bound for each variable(Optional)
    - osense:  Objective sense, e.g., "min" or "max" (Optional, defaults to "min")
    - csense:  Constraint senses, e.g., ["E", "L", "G"] for equality, ≤, ≥ (Optional, defaults to all "E")
"""

class LPModel(ArrowModel):
    def __init__(
        self,
        A: pa.RecordBatch,
        b: pa.Array,
        c: pa.Array,
        lb: pa.Array = None,
        ub: pa.Array = None,
        osense: pa.Scalar = None,
        csense: pa.Array = None
    ):
        """
    Initialize an LP model.

    Required:
            - A (RecordBatch): Sparse constraint matrix in COO format with "row", "col", "val"
            - b (Array): Right-hand side vector
            - c (Array): Objective function coefficients

        Optional:
            - lb (Array): Lower bounds (default: None, treated as unbounded)
            - ub (Array): Upper bounds (default: None, treated as unbounded)
            - osense (Scalar): "min" or "max" (default: "min")
            - csense (Array): ["E", "L", "G"] (default: all "E")

    Raises:
        TypeError / ValueError if inputs are malformed
    """
        if not isinstance(A, pa.RecordBatch):
            raise TypeError("A must be RecordBatch")
        if not all(name in A.schema.names for name in ["row", "col", "val"]):
            raise ValueError("A must contain 'row', 'col', and 'val' columns")

        self.A = A            # Sparse matrix in COO format (row, col, val)
        self.b = b            # Right-hand side vector
        self.c = c            # Objective function coefficients
        self.lb = lb    # Lower bounds for decision variables
        self.ub = ub    # Upper bounds for decision variables
        self.osense = osense if osense is not None else pa.scalar("min", type=pa.string())
        self.csense = csense if csense is not None else pa.array(["E"] * len(b), type=pa.string())
              
              
              
    def sanity_check(self):
        """
        Perform consistency checks on LP model dimensions and indices.

        This includes:
            - Shape consistency between variable vectors and bounds
            - Index validity in sparse matrix A
            - Constraint sense and objective sense validity

        Raises:
            ValueError: If any mismatch or invalid structure is detected.
        """
        n_vars = len(self.c)
        n_cons = len(self.b)

        # 1. Check sparse matrix A: row/col index validity
        check_arrow_coo_matrix("A", self.A, n_cons, n_vars)

        # 2. Check bounds (optional)
        check_variable_bounds(self.lb, self.ub, n_vars)

        # 3. Check csense (must match number of constraints)
        if len(self.csense) != n_cons:
            raise ValueError(f"Length of csense ({len(self.csense)}) != number of constraints ({n_cons})")
        for i, val in enumerate(self.csense):
            if val.as_py() not in {"E", "L", "G"}:
                raise ValueError(f"Invalid csense[{i}] = {val.as_py()} (must be one of 'E', 'L', 'G')")

        # 4. Check osense
        check_objective_sense(self.osense)
        
        
    # static method to create an LPModel from a dictionary representation
    @classmethod
    def from_dict(cls, model_dict: dict) -> "LPModel":
        """
        Create an LPModel instance from a dictionary representation.

        :param model_dict: Dictionary with keys 'A', 'b', 'c', 'lb', 'ub', 'osense', 'csense'
        :return: LPModel instance
        """
        A = pa.RecordBatch.from_pydict(model_dict["A"])
        b = pa.array(model_dict["b"])
        c = pa.array(model_dict["c"])
        lb = pa.array(model_dict.get("lb", []))
        ub = pa.array(model_dict.get("ub", []))
        osense = pa.scalar(model_dict.get("osense", "min"), type=pa.string())
        csense = pa.array(model_dict.get("csense", ["E"] * len(b)), type=pa.string())
        
        return cls(A, b, c, lb, ub, osense, csense)