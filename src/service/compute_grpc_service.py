"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
import pyarrow as pa
import pyarrow.flight
from utils.dict_to_pa_table import dict_to_pa_table
from service.base_service import BaseService

class GrpcComputeService(BaseService):
    """
    GrpcComputeService: gRPC client for compute service
    This service acts as a client to the gRPC compute service, allowing for
    computation requests to be sent and results to be received.
    It uses PyArrow to serialize and deserialize data for communication.
    It provides methods to compute models using the gRPC service.
    """
    def __init__(self):
        self.gRPC_ip = "127.0.0.1"
        self.gRPC_port = 8101
        super().__init__()


    def compute(self, model = None, solver = None, model_name = None) -> pa.Table:
        """Compute method implementation based on Flight gRPC

        Args:
            model (dict): The model to compute
            solver (dict): The solver configuration to use
            model_name (str, optional): Optional name for the model. Defaults to None.
        Returns:
            pa.Table: Result of the computation as a PyArrow Table
        """
        client = pyarrow.flight.connect(f"grpc://{self.gRPC_ip}:{self.gRPC_port}")
        client.as_async()
        print(client.supports_async)
        # Upload a new dataset
        request_dict = model.to_pydict()
        if "solver" not in request_dict:
            request_dict["solver"] = solver.__dict__
        message_table = dict_to_pa_table(request_dict)

        # Drop the old dataset
        param_str = f"pyomo_params_{model_name}"
        try:
            client.do_action(pa.flight.Action("drop_dataset", param_str.encode('utf-8')))
            upload_descriptor = pa.flight.FlightDescriptor.for_path(param_str)

            writer, reader = client.do_put(upload_descriptor, message_table.schema, options=pa.flight.FlightCallOptions(timeout=20))
            writer.write_table(message_table)
            writer.done_writing()
            _ = reader.read()
            get_param = "do_solver," + param_str + ",pyomo." + solver.solver_type.lower()
            # Compute the model and drop dataset from gRPC server
            result_reader = client.do_get(ticket=pa.flight.Ticket(get_param.encode('utf-8')))
            client.do_action(pa.flight.Action("drop_dataset", param_str.encode('utf-8')))
            res = result_reader.read_all()
            print("Received result from gRPC compute service===============:")
            print(res)
            return res
        except Exception as e:
            print(f"Error during gRPC compute: {e}")
            return pa.Table.from_pydict({"error_message": [str(e)]})
        finally:
            client.close()
