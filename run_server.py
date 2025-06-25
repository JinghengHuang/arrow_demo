import uvicorn, multiprocessing
from controller.arrow_rpc_server import grpc_serve_addr
import logging
import sys
import yaml
# Run all servers in multiprocessing

class GatewayServer():
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

    def run_server(self):
        self.logger = self.setup_custom_logger(f"worker_fastAPI")
        self.logger.info("Starting worker on FastAPI")
        uvicorn.run("controller.fastapi_restful:app",
                    host=self.ipaddr_http,
                    port=self.port,
                    # Auto reload, dev mode
                    reload=True, 
                    log_level="info",
                    access_log=True)
        
    def run_server_multiprocessing(self):
        server_thread = multiprocessing.Process(target=self.run_server, daemon=False)
        server_thread.start()
        server_thread.join()

# Run script to start http gateway server
if __name__ == "__main__":
    server = GatewayServer()
    server.config_loader()
    server.run_server()