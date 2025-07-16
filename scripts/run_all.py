"""
Run script to start the HTTP gateway server and engine servers together for debugging and testing.
"""
import multiprocessing
from run_server import GatewayServer
from run_julia_engine import JuliaEngineServer
from run_py_engine import PyEngineServer
# Run script to start http gateway server and engine server together, for debugging and testing
if __name__ == "__main__":
    server = GatewayServer()
    server.config_loader()
    py_engine_server = PyEngineServer()
    jl_engine_server = JuliaEngineServer()
    py_engine_server.config_loader()
    jl_engine_server.config_loader()
    jl_thread = multiprocessing.Process(target=jl_engine_server.run_julia_server, daemon=True)
    grpc_thread = multiprocessing.Process(target=py_engine_server.run_grpc_server, daemon=True)
    server_thread = multiprocessing.Process(target=server.run_server, daemon=False)
    server_thread.start()
    grpc_thread.start()
    jl_thread.start()
    server_thread.join()
    grpc_thread.join()
    jl_thread.join()
