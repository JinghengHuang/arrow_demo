from scipy.io import loadmat
from io import BytesIO
from scipy import sparse
import numpy as np
from objects.engine_model import EngineModel
import pyarrow as pa

# file = request.files["matfile"] ← get uploaded .mat file from a form field
# file_bytes = file.read()        ← read as bytes
# Then call this function to construct an EngineModel
def load_model_from_mat(file_bytes: bytes) -> 'EngineModel':
    # Load the .mat file from bytes using a BytesIO wrapper
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.loadmat.html
    data = loadmat(BytesIO(file_bytes))

    # Extract the model name — ignore default MATLAB metadata keys: '__header__', '__version__', '__globals__'
    model_names = [key for key in data.keys() if not key.startswith('__')]
    model_name = model_names[0]
    model_data = data[model_name]
    
    # Extract model components from the struct
    S =  sparse.csc_matrix(model_data['S'][0, 0])
    lb = np.array(_cell_to_float_list(model_data['lb'][0, 0]))
    ub = np.array(_cell_to_float_list(model_data['ub'][0, 0]))
    c = np.array(_cell_to_float_list(model_data['c'][0, 0]))
    b = np.array(_cell_to_float_list(model_data['b'][0, 0]))
    print([len(lb), len(ub), len(c), len(b)])
    rxns = _cell_to_str_list(model_data['rxns'][0, 0])
    mets = _cell_to_str_list(model_data['mets'][0, 0])
    # csense is a list of constraint senses, e.g., ["E", "L", "G"]
    # if not present assume all E
    csense = _cell_to_str_list(model_data['csense'][0, 0]) if 'csense' in model_data.dtype.names else pa.array(["E"] * len(b), type=pa.string())
    
    # Objective sense may be a string ("max"/"min") or numeric (1/-1)
    if "osenseStr" in model_data.dtype.names:
        val = model_data["osenseStr"][0, 0][0]
        osense = str(val) if isinstance(val, str) else str(val[0])
    elif "osense" in model_data.dtype.names:
        print(f"osense: {model_data['osense']}")
        val = float(model_data["osense"][0, 0][0][0])
        osense = "min" if val == 1 else "max"
    else:
        osense = "max"  # default to maximization
        
    S_coo = S.tocoo()
    S = pa.RecordBatch.from_arrays(
        [
            pa.array(S_coo.row.astype(np.int32)),  # row index
            pa.array(S_coo.col.astype(np.int32)),  # col index
            pa.array(S_coo.data.astype(np.float64))  # data values
        ],schema=pa.schema([
            ('row', pa.int32()),
            ('col', pa.int32()),
            ('data', pa.float64())
        ])
    )
    # convert to PyArrow arrays
    b = pa.array(b, type=pa.float64())
    c = pa.array(c, type=pa.float64())
    lb = pa.array(lb, type=pa.float64())
    ub = pa.array(ub, type=pa.float64())
    csense = pa.array(csense, type=pa.string()) if csense is not None else None
    osense = pa.scalar(osense, type=pa.string())
    
    # Construct and return the EngineModel object
    return EngineModel(model_name, S, b, c, lb, ub, osense, csense)



def _cell_to_str_list(arr):
    """Convert MATLAB cell array to a list of strings"""
    return [str(cell[0]) for cell in arr.squeeze()]

def _cell_to_float_list(arr):
    """"
    Convert MATLAB cell or numeric array to a list of floats
    """
    flat = np.atleast_1d(arr).squeeze()
    result = []
    for x in flat:
        try:
            val = float(x[0]) if isinstance(x, (np.ndarray, list)) else float(x)
            result.append(val)
        except Exception as e:
            print(f"Warning: cannot convert {x} to float: {e}")
            result.append(0.0)  
    return result


