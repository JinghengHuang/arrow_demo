"""
Run script to start the Julia engine server for optimization tasks.
"""
import multiprocessing
import logging
import sys
import os
import yaml
# Run all servers in multiprocessing

class JuliaEngineServer():
    """
    JuliaEngineServer class to run the Julia optimization engine server.
    This class is responsible for configuring the Julia server, setting up logging,
    and running the Julia engine in a separate process.
    It reads configuration from a YAML file to determine the IP address and port for the Julia server
    """
    def __init__(self):
        self.julia_port = 65432
        self.ipaddr_julia = "0.0.0.0"


    def config_loader(self):
        """
        Load config from config.yaml
        will load ip and port config for Julia
        """
        with open('config.yaml', 'r', encoding='utf-8') as file:
            nested_data = yaml.safe_load(file)
            if nested_data["julia"] is not None:
                self.julia_port = int(nested_data["julia"]["port"])
                self.ipaddr_julia = nested_data["julia"]["ip"]

    def setup_custom_logger(self, name:str):
        """Set custom logger for a subprocess

        Args:
            name (str): Name of the logger

        Returns:
            Logger: Logger object
        """
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
        """ Using system command to run julia, requires julia environment in the system
        """
        os.system(f'julia --project=src/service/optimization_service/julia src/service/optimization_service/julia/engine.jl {self.ipaddr_julia} {self.julia_port}')

  
    def start_engine_services(self) -> None:
        """Run julia service in a separate process
        """
        julia_thread = multiprocessing.Process(target=self.run_julia_server, daemon=True)
        # Fon now, only FastAPI server, expand on gRPC if needed
        julia_thread.start()
        julia_thread.join()

# Run script to start engine service
if __name__ == "__main__":
    server = JuliaEngineServer()
    server.config_loader()
    server.start_engine_services()
