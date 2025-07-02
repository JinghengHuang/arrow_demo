include("optimization_server.jl")
using .OptimizationServer

# Start the server
host = "127.0.0.1"
port = 65432
start_server(host, port)