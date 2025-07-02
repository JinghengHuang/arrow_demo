import multiprocessing
from service.optimization_service.arrow_rpc_server import grpc_serve_addr
import logging
import sys, os
import yaml
# Run all servers in multiprocessing

class JuliaEngineServer():
    def __init__(self):
        pass
        
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
    
    
    def run_julia_server(self):
        os.system('julia --project=./ src/service/optimization_service/julia/engine.jl')
    
        
    # TODO Add other service starting points here
    def start_engine_services(self) -> None:
        julia_thread = multiprocessing.Process(target=self.run_julia_server, daemon=True)
        # Fon now, only FastAPI server, expand on gRPC if needed
        julia_thread.start()
        julia_thread.join()

# Run script to start engine service
if __name__ == "__main__":
    server = JuliaEngineServer()
    server.config_loader()
    server.start_engine_services()