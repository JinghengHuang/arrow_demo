import numpy as np
import pyarrow as pa
from pyarrow import ipc
import io

class Model:
    
    """
    Converts mat file to arrow
    """
    def __init__(self, model_name, S, lb, ub, c, rxns, mets, osense, csense):
        self.model_name = model_name
        self.S = S  # Stoichiometric matrix
        self.lb = lb  # Lower bounds
        self.ub = ub  # Upper bounds
        self.c = c  # Objective coefficients
        self.rxns = rxns  # Reactions
        self.mets = mets  # Metabolites
        self.osense = osense  # Optimization sense ('max' or 'min')
        self.csense = csense  # Constraint sense
    
    
    @staticmethod
    def _to_ipc_bytes(table: pa.Table) -> bytes:
        sink = io.BytesIO()
        with ipc.new_stream(sink, table.schema) as w:
            w.write_table(table)
        return sink.getvalue()
    
    def to_arrow(self):
        """
        Convert the model to an Arrow table.
        """
        
        S_csc = self.S
        S_coo = S_csc.tocoo() # 转换为 COO 格式
        nrow, ncol = S_coo.shape

        S_row_tbl = pa.table({"row": S_coo.row.astype(np.int64)})
        S_col_tbl = pa.table({"col": S_coo.col.astype(np.int64)})
        S_data_tbl= pa.table({"data": S_coo.data})
        
        # 将数据转换为 Arrow 表 
        lb_tbl = pa.table({"lb": self.lb})
        ub_tbl = pa.table({"ub": self.ub})
        c_tbl  = pa.table({"c":  self.c})
        
        S_row_b = Model._to_ipc_bytes(S_row_tbl)
        S_col_b = Model._to_ipc_bytes(S_col_tbl)
        S_data_b= Model._to_ipc_bytes(S_data_tbl)

        lb_b = Model._to_ipc_bytes(lb_tbl)
        ub_b = Model._to_ipc_bytes(ub_tbl)
        c_b  = Model._to_ipc_bytes(c_tbl)
        return S_row_b, S_col_b, S_data_b,nrow, ncol,lb_b, ub_b, c_b
        