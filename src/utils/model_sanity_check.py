"""
Utility functions to validate sparse matrix formats and variable bounds in PyArrow RecordBatches.
"""
import pyarrow.compute as pc
import pyarrow as pa

def check_arrow_coo_matrix(name, batch, num_rows, num_cols):
    """
    Validate a sparse matrix in COO format (stored as RecordBatch).
    
    Checks:
        1. "row", "col", "val" exist
        2. row indices < num_rows
        3. col indices < num_cols
        4. max(row) + 1 == num_rows  (tight row range check)
    
    Args:
        name (str): Name of the matrix (e.g., "A", "Q")
        batch (pa.RecordBatch): Sparse matrix in COO format
        num_rows (int): Expected number of rows (i.e., constraint or variable count)
        num_cols (int): Expected number of cols (i.e., variable count)
    
    Raises:
        ValueError: If format or index is invalid
    """
    if batch is None or batch.num_rows == 0:
        return

    max_row = pc.max(batch["row"]).as_py()
    max_col = pc.max(batch["col"]).as_py()

    if max_row >= num_rows:
        raise ValueError(f"{name} row index {max_row} exceeds number of rows {num_rows}")
    if max_col >= num_cols:
        raise ValueError(f"{name} col index {max_col} exceeds number of columns {num_cols}")
    if max_row + 1 != num_rows:
        raise ValueError(f"{name} row indices do not span a tight range: expected max row {num_rows - 1}, got {max_row}")


def check_variable_bounds(lb: pa.Array, ub: pa.Array, n_vars: int):
    """
    Check that variable bounds (lb and ub) match expected number of variables.

    Args:
        lb (pa.Array or None): Lower bounds
        ub (pa.Array or None): Upper bounds
        n_vars (int): Expected length of bounds

    Raises:
        ValueError: If lb or ub is provided but length mismatches
    """
    if lb is not None and len(lb) != n_vars:
        raise ValueError(f"Length of lb ({len(lb)}) != number of variables ({n_vars})")
    if ub is not None and len(ub) != n_vars:
        raise ValueError(f"Length of ub ({len(ub)}) != number of variables ({n_vars})")



def check_objective_sense(osense: pa.Scalar):
    """
    Check if objective sense is valid ('min' or 'max').

    Args:
        osense (pa.Scalar): Objective sense scalar

    Raises:
        ValueError: If value is not 'min' or 'max'
    """
    if osense.as_py() not in {"min", "max"}:
        raise ValueError(f"osense must be 'min' or 'max', got '{osense.as_py()}'")
