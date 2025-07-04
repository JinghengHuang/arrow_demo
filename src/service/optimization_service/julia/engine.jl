include("optimization_server.jl")
using .OptimizationServer

# Start the server, taking arguments (first is IP, second is port)
host = ARGS[1]
port = parse(Int64, ARGS[2])
start_server(host, port)