import pyarrow as pa
import pyarrow.compute as pc


class LPModel:
    def __init__(
        self,
        model_name: str,
        S: pa.RecordBatch,
        b: pa.Array,
        c: pa.Array,
        lb: pa.Array,
        ub: pa.Array,
        osense: pa.Scalar,
        csense: pa.Array
    ):
        # Ensure that S is a valid RecordBatch
        if not isinstance(S, pa.RecordBatch):
            raise TypeError("S must be a pyarrow RecordBatch")

        # Ensure that required columns exist in S: row indices, column indices, and data
        for name in ["row", "col", "data"]:
            if name not in S.schema.names:
                raise ValueError(f"S must contain column '{name}'")

        self.model_name = model_name
        self.S = S            # Sparse matrix in COO format (row, col, data)
        self.b = b            # Right-hand side vector
        self.c = c            # Objective function coefficients
        self.lb = lb          # Lower bounds
        self.ub = ub          # Upper bounds
        self.osense = osense  # Objective sense (e.g., "max" or "min")
        self.csense = csense  # Constraint senses (e.g., ["E", "L", "G"])     
        

    def to_pydict(self):
        """
        Convert the model to Arrow IPC binary blocks for transmission.
        Returns:
            A dictionary mapping each component name to its serialized Arrow IPC bytes:
                - "S":     Sparse matrix in COO format (RecordBatch with "row", "col", "data")
                - "S_shape": RecordBatch with matrix shape: "nrow", "ncol"
                - "b", "c", "lb", "ub", "csense": RecordBatches
                - "osense": Scalar (wrapped and serialized)
        """
        row = self.S["row"]
        col = self.S["col"]
        data = self.S["data"]

        # Create a RecordBatch for the sparse matrix S
        # with columns: "row", "col", "data"
        # and a RecordBatch for the shape of S with "nrow", "ncol
        S_batch = pa.record_batch({
            "row": row,
            "col": col,
            "data": data
        })
        
        return {
            "S": S_batch,
            "b": self.b,
            "c": self.c,
            "lb": self.lb,
            "ub": self.ub,
            "osense": self.osense,
            "csense": self.csense
        }
    
        
        
    