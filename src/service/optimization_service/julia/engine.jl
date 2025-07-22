include("controller/socket_server.jl")

# This is the entry point for the Julia optimization service.
# It starts the TCP server.
try
    host = length(ARGS) >= 1 ? ARGS[1] : "127.0.0.1"
    port = length(ARGS) >= 2 ? parse(Int, ARGS[2]) : 65432
    SocketServer.start_server(host, port)
catch e
    @error "Failed to start server: $e"
end
