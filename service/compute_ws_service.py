"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
from service.base_service import BaseService
import pyarrow as pa
import json
from pyarrow import json as pajson
import pyarrow.flight
from objects.engine_model import EngineModel
from utils.mat_parser import load_model_from_mat

class WsComputeService(BaseService):
    def __init__(self):
        self.gRPC_ip = "127.0.0.1"
        self.gRPC_port = 8101
        super().__init__()
    
                    
    def compute(self, model_bin = None) -> pa.Table:
        client = pa.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        # Upload a new dataset(test data)
        data = load_model_from_mat(model_bin)
        ipc = data.to_ipc_bytes()

        upload_descriptor = pa.flight.FlightDescriptor.for_path("python_glpk_param")
        writer, _ = client.do_put(upload_descriptor, ipc.schema)
        writer.write_table(ipc)
        writer.close()


        # Retrieve metadata of newly uploaded dataset
        flight = client.get_flight_info(upload_descriptor)
        descriptor = flight.descriptor

        # Read content of the dataset
        reader = client.do_get(flight.endpoints[0].ticket)
        read_table = reader.read_all()

        # Drop the newly uploaded dataset

        result_reader = client.do_get(pa.flight.Ticket(b"do_solver,python_glpk_param,pyomo.glpk_solver_example"))
        client.do_action(pa.flight.Action("drop_dataset", "python_glpk_param".encode('utf-8')))

        return result_reader.read_all()
