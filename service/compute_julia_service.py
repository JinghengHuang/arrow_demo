"""
Service class that acts as a gRPC client between gateway and engine gRPC service
"""
from service.base_service import BaseService
import pyarrow as pa
import socket
from utils.mat_parser import load_model_from_mat
from utils.dict_to_pa_table import dict_to_pa_table

class JuliaComputeService(BaseService):
    def __init__(self):
        self.julia_ip = "127.0.0.1"
        self.julia_port = 65432
        super().__init__()
    
                    
    def compute(self, model_bin = None, solver = None) -> pa.Table:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.julia_ip, self.julia_port))
            # Send the model binary to the Julia service
            model = load_model_from_mat(model_bin)
            model_ipc_dict= model.to_pydict()
            solver_ipc_dict = solver.to_pydict()
            message_table = dict_to_pa_table(model_ipc_dict).append_column("solver", dict_to_pa_table(solver_ipc_dict))
            print(f"schema of message_table: {message_table.schema}")
            
            print(f"Sending model to Julia service: {message_table.schema.names}")
            print(f"type of each column: {[message_table.column(i).type for i in range(len(message_table.schema))]}")
            # turn the table to IPC bytes
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, message_table.schema) as writer:
                writer.write(message_table)
            # framing: send the length of the message first
            client_socket.sendall(len(sink.getvalue()).to_bytes(4, byteorder='little', signed=True))
            print(f"Sent length of message: {len(sink.getvalue())} bytes")
            client_socket.sendall(sink.getvalue())
            print("Sent 'END' marker to Julia")

            pass
            # while True:
            #     # Receive the response from the Julia service
            #     response = client_socket.recv(4096)
            #     if not response:
            #         break
            #     print(f"<<< Received response from Julia service: {response}")
            # # Receive the result from the Julia service
            # return response
