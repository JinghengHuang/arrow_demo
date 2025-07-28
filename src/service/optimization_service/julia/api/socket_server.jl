"""
SocketServer module provides the functionality to start a TCP server for handling optimization requests.
It listens for incoming connections and processes optimization requests asynchronously.
"""
module SocketServer

using Sockets
include("../utils/io_utils.jl")
include("../service/optimization_service.jl")

export start_server


"""
    start_server(host::String, port::Int)

Starts the optimization server and listens for client connections via TCP.

# Arguments
- `host::String`: IP address or hostname to bind the server to (e.g., "127.0.0.1").
- `port::Int`: TCP port to listen on (e.g., 65432).

# Behavior
- Accepts incoming socket connections in a loop.
- Spawns an asynchronous task (`@async`) for each client to handle its request.

# Example
```julia
start_server("127.0.0.1", 65432)
````
"""
function start_server(host::String, port::Int)
    server = listen(IPv4(host), port)
    @info "Optimization server started on $host:$port"

    while true
        client = accept(server)
        client_ip, client_port = getpeername(client)
        @info "Accepted client connection from address: $client_ip:$client_port"
        @async handle_request(client)
    end
end


"""
    handle_request(client::TCPSocket)
    Handles a single optimization request from a client.
    This function reads the optimization data from the client, processes it using the `OptimizationService`, and sends back the result.

    # Workflow
    1. Reads optimization data from the client using `IOUtils.read_data_from_client`.
    2. Calls `OptimizationService.optimize` to perform the optimization.
    3. Sends the optimization result back to the client using `IOUtils.send_success_result`.
    4. Catches any errors during processing and sends a failure result back to the client.
    5. Closes the client socket after processing.

    # Arguments
    - `client::TCPSocket`: The client socket connected to the server.

    # Example
    ```julia
    handle_request(optimization_client)
    ```
    # Note
    Automatically closes the client socket after processing.
"""
function handle_request(client::TCPSocket)
    try
        data_dict = IOUtils.read_data_from_client(client)
        status, objval, sol = OptimizationService.optimize(data_dict)
        IOUtils.send_success_result(client, status, objval, sol)
    catch e
        @error "Error handling optimization request: $(e)"
        IOUtils.send_failure_result(client, e)
    finally
        close(client)
    end
end

end  # module SocketServer
