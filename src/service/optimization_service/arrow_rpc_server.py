import pathlib
import pyarrow as pa
import pyarrow.flight
from service.optimization_service.solver_factory import SolverFactory
import logging
import sys
from utils.dict_to_pa_table import dict_to_pa_table, unpack_pa_table_dict
from concurrent.futures import ThreadPoolExecutor
import threading

solver_factory = SolverFactory()
logger = logging.getLogger(__name__)

class FlightServer(pyarrow.flight.FlightServerBase):

    def __init__(self, location="grpc://0.0.0.0:8815",
                repo=pathlib.Path("./datasets"), **kwargs):
        super(FlightServer, self).__init__(location, **kwargs)
        self._location = location
        self._repo = repo
        self._tables:dict = {}
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _make_flight_info(self, dataset):
        with self._lock:
            table = self._tables[dataset]
            schema = table.schema
            descriptor = pa.flight.FlightDescriptor.for_path(
                dataset.encode('utf-8')
            )
            endpoints = [pa.flight.FlightEndpoint(dataset, [self._location])]
            return pyarrow.flight.FlightInfo(schema,
                                            descriptor,
                                            endpoints,-1,-1)

    def list_flights(self, context, criteria):
        for dataset in self._repo.iterdir():
            yield self._make_flight_info(dataset.name)

    def get_flight_info(self, context, descriptor):
        return self._make_flight_info(descriptor.path[0].decode('utf-8'))

    def do_put(self, context, descriptor, reader, writer):
        dataset:str = descriptor.path[0].decode('utf-8')
        data_table = reader.read_all()
        problem = ""
        key = ""
        with self._lock:
            if dataset.find(":") > 0:
                problem = dataset.split(":")[0]
                key = dataset.split(":")[1]
                try:
                    if problem in self._tables:
                        self._tables[problem][key] = data_table
                    else:
                        self._tables[problem] = {}
                        self._tables[problem][key] = data_table
                except KeyError:
                    self._tables[problem] = {}
                    self._tables[problem][key] = data_table
            else:
                self._tables[dataset] = data_table

    def do_get(self, context, ticket):
        with self._lock:
            ticket_str:str = ticket.ticket.decode('utf-8')
            # handle do solvers
            if ticket_str.find("do_solver") != -1:
                future = self.executor.submit(self.do_solver, ticket_str)
                try:
                    # set a timeout
                    return future.result(timeout=30) 
                except Exception as e:
                    logger.error(f"Solver execution failed: {e}")
                    raise pa.flight.FlightServerError(f"Solver error: {e}")
            # default endpoint
            else:
                return pa.flight.RecordBatchStream(self._tables[ticket_str])

    def list_actions(self, context):
        return [
            ("drop_dataset", "Delete a dataset."),
        ]

    def do_action(self, context, action):
        if action.type == "drop_dataset":
            return self.do_drop_dataset(action.body.to_pybytes().decode('utf-8'))
        else:
            raise NotImplementedError

    # Drop all dataset related to a task
    def do_drop_dataset(self, dataset):
        with self._lock:
            self._tables[dataset] = None
    # Execute a solver
    def do_solver(self, param:str):
        params = param.split(',')
        dataset = params[1]
        solver_name = params[2]
        # get data from memory
        input_params:dict = unpack_pa_table_dict(self._tables.get(dataset))
        # get solver
        solver = solver_factory.get_solver(solver_name)
        # run solver and get result in form of pa table
        logger.info("Computing model:")
        result = solver.run(input_params)
        logger.info(result)
        result_table = dict_to_pa_table(result)
        return pa.flight.RecordBatchStream(result_table)

def grpc_serve_addr(ipaddr:str, port:int, ext_logger) -> None:
    logger = ext_logger
    if ipaddr is not None and port is not None:
        server = FlightServer(location=f"grpc://{ipaddr}:{port}")
    else:
        server = FlightServer()
    server._repo.mkdir(exist_ok=True)
    logger.info("Server running at " + server._location)
    server.serve()
# Use when run standalone
def grpc_serve() -> None:
    server = FlightServer()
    server._repo.mkdir(exist_ok=True)
    logger.info("Server running at " + server._location)
    server.serve()

if __name__ == '__main__':
    # logging conf
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    logger.info("Starting gRPC server...")
    # start the gRPC server
    grpc_serve()