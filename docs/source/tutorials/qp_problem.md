# Quadratic Programming (QP) Problems in OptArrow

OptArrow provides an efficient optimization service using the Apache Arrow IPC format for inter-process communication. This document explains how to structure and send a Quadratic Programming (QP) problem to the OptArrow engine using Python.

## Standard QP Form

The QP problem should be structured as:

```
minimize     1/2 xᵀ Q x + cᵀ x
subject to   A x = b            (equality constraints)
            G x <= h           (inequality constraints)
            lb <= x <= ub      (bounds)
```

### Model Components

* **Q**: Quadratic coefficient matrix (symmetric), stored as a sparse COO format with `row`, `col`, `val`
* **c**: Linear objective vector
* **A**: Equality constraint matrix (sparse COO)
* **b**: Right-hand side of equality constraints
* **G**: (Optional) Inequality constraint matrix (sparse COO)
* **h**: (Optional) Right-hand side of inequality constraints
* **lb**: (Optional) Lower bounds for each variable
* **ub**: (Optional) Upper bounds for each variable
* **osense**: (Optional) Objective sense: "min" or "max" (default is "min")

## IPC Request Structure (`ipc_dict`)

The message to OptArrow should be structured as follows:

```python
ipc_dict = {
    "model": model_data,       # The QP model data structure (see below)
    "model_name": "test_qp",   # Optional: model identifier
    "engine": "julia",         # Engine used for computation
    "solver": solver_config    # Solver configuration
}
```

### `model` (Required)

QP model structured as a dictionary:

```python
model_data = {
    "Q": {
        "row": [...],     # Row indices for Q (symmetric matrix)
        "col": [...],     # Column indices for Q
        "val": [...]      # Values at (row, col)
    },
    "c": [...],           # Linear coefficients
    "A": {
        "row": [...],
        "col": [...],
        "val": [...]
    },
    "b": [...],           # RHS of equality constraints
    "G": {                # (Optional) Inequality matrix
        "row": [...],
        "col": [...],
        "val": [...]
    },
    "h": [...],           # (Optional) RHS of inequality constraints
    "lb": [...],          # (Optional) Lower bounds
    "ub": [...],          # (Optional) Upper bounds
    "osense": "min"       # (Optional) "min" or "max"
}
```

### `solver` (Required)

```python
solver = {
    "solver_name": "OSQP",       # Example solver name
    "solver_type": "QP",         # Solver type
    "solver_params": {            # (Optional) solver-specific params
        "time_limit": 30,
        "eps_abs": 1e-5
    }
}
```

### `model_name` (Optional)

For logging or traceability.

### `engine` (Required)

Specifies the backend system to be used for computation. Currently supports `"julia"` and `"python"`.

## Data Packaging with Apache Arrow

```python
ipc_table = dict_to_pa_table(ipc_dict)

sink = pa.BufferOutputStream()
with pa.ipc.new_stream(sink, ipc_table.schema) as writer:
    writer.write(ipc_table)

ipc_bytes = sink.getvalue().to_pybytes()
```

## Sending the Request

```python
headers = {
    "Content-Type": "application/vnd.apache.arrow.stream"
}

response = requests.post(url, data=ipc_bytes, headers=headers)
```

## Response

```python
reader = pa.ipc.open_stream(response.content)
result_table = reader.read_all()
```

## Notes

* Ensure symmetric structure in Q.
* G and h are optional; omit them for pure equality-constrained QP.
* Schema consistency is crucial; use Arrow types that match server expectations.
* Typical QP solvers include Gurobi, and Mosek.

