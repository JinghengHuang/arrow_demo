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
    
                    
    def compute(self, model_bin = None, solver = None) -> pa.Table:
        client = pa.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        client.as_async()
        print(client.supports_async)
        # Upload a new dataset(test data)
        # Not as a COO sparse matrix
        model = load_model_from_mat(model_bin)
        model_ipc_dict= model.to_pydict()
        solver_ipc_dict = solver.to_pydict()
        message_table = dict_to_pa_table(model_ipc_dict).append_column("solver", dict_to_pa_table(solver_ipc_dict))
        print(f"schema of message_table: {message_table.schema}")
        
        print(f"Sending model to Pyomo service: {message_table.schema.names}")
        print(f"type of each column: {[message_table.column(i).type for i in range(len(message_table.schema))]}")
        # Drop the old dataset
        try:
            client.do_action(pa.flight.Action("drop_dataset", "cobra_lp_params".encode('utf-8')))
            upload_descriptor = pa.flight.FlightDescriptor.for_path(f"cobra_lp_params")
            
            print(f"Sending Data:")
            writer, reader = client.do_put(upload_descriptor, message_table.schema, options=pa.flight.FlightCallOptions(timeout=20))
            writer.write_table(message_table)
            writer.done_writing()
            _ = reader.read()
            # Compute the model and drop dataset from gRPC server
            result_reader = client.do_get(ticket=pa.flight.Ticket(b"do_solver,cobra_lp_params,pyomo.cobra_lp")
                                        #   , options=pa.flight.FlightCallOptions(timeout=20)
                                          )
            client.do_action(pa.flight.Action("drop_dataset", "cobra_lp_params".encode('utf-8')))
            res = result_reader.read_all()
            return res
        except Exception as e:
            print(e)
        finally:
            print(f"Connection closed:")
            client.close()
