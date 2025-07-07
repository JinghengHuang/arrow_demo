module OptimizationServer
using JuMP
using HiGHS
using Sockets
using Arrow
using SparseArrays
using DataFrames

include("registry.jl")
include("lp.jl")
include("qp.jl")
using .Registry


# Export the functions
export start_server

# register the model builder function
Registry.register_model("LP", (data) -> LPModel.build_jump_model(data))
Registry.register_model("QP", (data) -> QPModel.build_jump_model(data))

"""
    start_server(host::String, port::Int)

Starts the server and listens for client connections on the specified `host` and `port`.

# Arguments
- `host::String`: The IP address or hostname where the server will listen for connections.
- `port::Int`: The port number on which the server will listen.

# Example
```julia
start_server("127.0.0.1", 65432)
```
"""
function start_server(host::String, port::Int)
    server = listen(IPv4(host), port)
    println("Listening on $host:$port")

    while true
        client = accept(server)
        client_ip, client_port = getpeername(client)
        println("Accepted client connection from address: $client_ip: $client_port")
        @async handle_optimization_request(client)
    end
end

"""
    handle_optimization_request(client::TCPSocket)

Handles optimization requests from the given client. Processes the received data to form an LP problem,
runs optimization using COBRA.jl, and sends results back to the client.

# Arguments
- `client::TCPSocket`: The client socket connected to the server.
# Example
```julia
# Assuming optimization_client is a connected TCPSocket
handle_optimization_request(optimization_client)

```
"""
function handle_optimization_request(client)
    try
        while true
            data_dict = read_data_from_client(client)
            problem_type = uppercase(get_problem_type(data_dict))
            builder = Registry.get_builder(problem_type)
            if builder === nothing
                error("Problem type $problem_type not supported by the server.")
            end
            model, x, c = builder(data_dict)
            # send success result to client
            start_time = time()
            status, objval, sol = solve(model, x)
            end_time = time()
            @info "Time taken to solve the LP problem in COBRA.jl: $(end_time - start_time) seconds."
            send_success_result(client, status, objval, sol)
        end
    catch e
        send_failure_result(client, e)
        rethrow(e)
    finally
        close(client)
        println("Closed connection")
    end
end

"""
    read_data_from_client(client::TCPSocket) :: Dict{Symbol, Arrow.Table}

Reads and deserializes Arrow IPC data from the given client and returns it as a dictionary.

# Arguments
-   `client::TCPSocket`: The client socket from which to read data.
# Return
- `Dict{Symbol, Arrow.Table}`: A dictionary where keys are symbols representing table names and values are Arrow.Tables.
# Example
```julia
data_dict = read_data_from_client(client)
```
"""
function read_data_from_client(client)
    tables = Dict{Symbol,Any}()
    header = read(client, UInt32)  # Read the fixed-length header
    data_length = Int(header)

    data = read(client, data_length)

    # Deserialize Arrow IPC data
    buf = IOBuffer(data)
    table = Arrow.Table(buf)

    for key in keys(table)
        column = table[key][1]
        tables[key] = column
    end
    return tables
end


function get_problem_type(data)
    solver_dict = Dict{Symbol,Any}()
    solver_table = data[:solver]
    solver_name = solver_table[:solver_name]
    problem_type = solver_table[:solver_type]
    # solver_params_vector = Vector{Tuple{String, Any}}(solver_table[:parameters])
    # solver[:parameters] = solver_params_vector
    # solver = SolverConfig(solver_name, solver_params_vector)
    return problem_type
end


function solve(model, x)
    optimize!(model)
    return (
        status=termination_status(model),
        objval=objective_value(model),
        sol=value.(x)
    )
end



"""
    send_success_result(client::Sockets.Socket, lpProblem::COBRA.LPproblem, status::MathOptInterface.TerminationStatusCode, objval::Float64, sol::Vector{Float64})

Sends the results of an optimization problem back to the client upon successful completion. The function constructs and sends several data tables, including the main results, the status of the optimization, and the objective value.

# Arguments
- `client::Sockets.Socket`: The client socket to which the results will be sent.
- `lpProblem::COBRA.LPproblem`: The linear programming problem that was solved.
- `status::MathOptInterface.TerminationStatusCode`: The status of the optimization process.
- `objval::Float64`: The objective value obtained from the optimization.
- `sol::Vector{Float64}`: The solution vector obtained from the optimization.

# Example
```julia
# Assuming `client` is a valid Sockets.Socket, and `lpProblem`, `status`, `objval`, and `sol` are defined
send_success_result(client, lpProblem, status, objval, sol)
```
"""
function send_success_result(client, status, objval, sol)
    # Create a DataFrame with the results

    result = [(; success=true, status=string(status), objective_value=objval, solution=[sol])]


    try
        # result_table = Arrow.Table(result)
        buf = IOBuffer()
        Arrow.write(buf, result)

        ipc_bytes = take!(buf)
        write(client, UInt32(length(ipc_bytes)))
        write(client, ipc_bytes)

    catch e
        @error "Failed to create Arrow.Table from DataFrame: $(e)"
    end
    # Send result back to client
    # send_result(client, ipc_bytes)
end

"""
    send_failure_result(client::Sockets.Socket, error::Exception)

Sends the results of a failed optimization attempt back to the client. The function constructs and sends a data table containing an error message indicating the failure of the optimization process.

# Arguments
- `client::Sockets.Socket`: The client socket to which the error result will be sent.
- `error::Exception`: The exception that was raised during the optimization process. This exception message will be included in the response to the client.

# Example
```julia
# Assuming `client` is a valid Sockets.Socket and `error` is an Exception object
send_failure_result(client, error)
```
"""
function send_failure_result(client, error)
    failure_table = DataFrame(success=false, error_message=string(error))
    # Send result back to client
    send_result(client, failure_table)
    send_end_marker(client)
end


"""
    send_end_marker(client::Sockets.Socket)

Sends an end marker to the client to indicate that no more data will follow. The end marker is a fixed-length header with a value of zero, which is used to signal the end of the data stream.

# Arguments
- `client::Sockets.Socket`: The client socket through which the end marker will be sent.

# Example
```julia
# Assuming `client` is a valid Sockets.Socket
send_end_marker(client)
```
"""
function send_end_marker(client)
    write(client, UInt32(0))  # Send a header with length 0 to indicate the end
end



end  # module

