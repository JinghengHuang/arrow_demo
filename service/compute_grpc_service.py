"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
from service.base_service import BaseService
import pyarrow as pa
import json
from pyarrow import json as pajson
import pyarrow.flight
from utils.mat_parser import load_model_from_mat
from utils.dict_to_pa_table import dict_to_pa_table

class GrpcComputeService(BaseService):
    def __init__(self):
        self.gRPC_ip = "127.0.0.1"
        self.gRPC_port = 8101
        super().__init__()
    
                    
    def compute(self, model_bin = None) -> pa.Table:
        client = pa.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        # Upload a new dataset(test data)
        data = load_model_from_mat(model_bin)
        ipc = data.__dict__
        # Convert to pyTable for shipping via Flight
        data_table = dict_to_pa_table(ipc)
        
        upload_descriptor = pa.flight.FlightDescriptor.for_path(f"cobra_lp_params")
        writer, reader = client.do_put(upload_descriptor, data_table.schema)
        writer.write_table(data_table)
        writer.close()
        # Compute the model and drop dataset from gRPC server
        result_reader = client.do_get(pa.flight.Ticket(b"do_solver,cobra_lp_params,pyomo.cobra_lp"))
        client.do_action(pa.flight.Action("drop_dataset", "cobra_lp_params".encode('utf-8')))

        return result_reader.read_all()
