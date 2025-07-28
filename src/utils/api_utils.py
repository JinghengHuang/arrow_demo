import pyarrow as pa
from model.request_model import RequestModel

def validate_request_input(table: pa.Table) -> bool:
    """Check if input is in the right form, based on the class RequestModel

    Args:
        table (pa.Table): table to check

    Returns:
        bool: If the input is valid
    """
    keys = table.column_names
    required_keys = vars(RequestModel()).keys()
    if all(key in keys for key in required_keys):
        return True
    return False

def write_table_to_ipc_bytes(table:pa.Table) -> bytes:
    """Write PyArrow Table data to ipc bytes for returning via HTTPS

    Args:
        table (pa.Table): Table data

    Returns:
        bytes: ipc bytes
    """
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write(table)
    ipc_bytes = sink.getvalue().to_pybytes()
    return ipc_bytes