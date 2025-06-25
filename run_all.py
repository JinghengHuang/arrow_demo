from run_server import GatewayServer
from run_engine_service import EngineServer
import multiprocessing
# Run script to start http gateway server and engine server together, for debugging and testing
if __name__ == "__main__":
    server = GatewayServer()
    server.config_loader()
    engine_server = EngineServer()
    engine_server.config_loader()
    grpc_thread = multiprocessing.Process(target=engine_server.run_grpc_server, daemon=True)
    server_thread = multiprocessing.Process(target=server.run_server, daemon=False)
    server_thread.start()
    grpc_thread.start()
    server_thread.join()
    grpc_thread.join()