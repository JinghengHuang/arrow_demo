import multiprocessing
from controller.arrow_rpc_server import grpc_serve_addr
import logging
import sys
import yaml
# Run all servers in multiprocessing

class EngineServer():
    def __init__(self):
        self.port = 8000
        self.grpc_port = 8100
        self.ipaddr_http = "127.0.0.1"
        self.ipaddr_rpc = "127.0.0.1"
        
    def config_loader(self):
        with open('config.yaml', 'r') as file:
            nested_data = yaml.safe_load(file)
            if nested_data["http"] is not None:
                self.port = int(nested_data["http"]["port"])
                self.ipaddr_http = nested_data["http"]["ip"]
            if nested_data["grpc"] is not None:
                self.grpc_port = int(nested_data["grpc"]["port"])
                self.ipaddr_rpc = nested_data["grpc"]["ip"]

    def setup_custom_logger(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(f'%(levelname)s:     %(message)s')
        handler.setFormatter(formatter)
        # Avoid adding multiple handlers if re-run
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        return self.logger
    
    
    def run_grpc_server(self):
        logger = self.setup_custom_logger(f"worker_grpc")
        logger.info("Starting worker on gRPC server")
        grpc_serve_addr(self.ipaddr_rpc, self.grpc_port, logger)
        
    # TODO Add other service starting points here
    def start_engine_services(self) -> None:
        grpc_thread = multiprocessing.Process(target=self.run_grpc_server, daemon=True)
        # Fon now, only FastAPI server, expand on gRPC if needed
        grpc_thread.start()
        grpc_thread.join()

# Run script to start engine service
if __name__ == "__main__":
    server = EngineServer()
    server.config_loader()
    server.start_engine_services()