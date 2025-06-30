module OptimizationServer
using JuMP
using HiGHS
using Sockets
using Arrow
using SparseArrays
using DataFrames

# use solve.jl
script_path = @__FILE__
script_dir = dirname(script_path)
include(joinpath(script_dir, "solve.jl"))


# Export the functions
export start_server


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
            model, x, c = form_model(data_dict)
            # send success result to client
            start_time = time()
            status, objval, sol = solvelp(model, x)
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
    println("Received data length: ", data_length)

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

"""
    get_solver(data::Dict{Symbol, Any}) :: Dict{Symbol, Any}

Extracts the solver name and parameters from the provided data dictionary.

# Arguments
- `data::Dict{Symbol, Any}`: A dictionary containing solver information.
# Returns
- `Dict{Symbol, Any}`: A dictionary with keys :name (solver name as a string) and :parameters (solver parameters as a vector of tuples).
# Example
```julia
solver = get_solver(data_dict)
```
"""
function get_solver(data)
    solver_dict = Dict{Symbol,Any}()
    solver = data[:solver][:solver]

    # solver = Dict{Symbol,Any}()
    # # Extracts and processes the solver name.
    # solver_name_data = data[:solver][:solver_name]
    # solver_name = join(collect(skipmissing(solver_name_data)))

    # # processes the solver parameters.
    # solver_params_vector = []
    # if haskey(data[:solver], :solver_params)
    #     solver_params = data[:solver][:solver_params]
    #     for param in solver_params
    #         if !ismissing(param)
    #             for (k, v) in pairs(param)
    #                 if !ismissing(v)
    #                     push!(solver_params_vector, (k, v))
    #                 end
    #             end
    #         end
    #     end
    # end

    # A dictionary holding both the solver name and parameters.
    solver[:name] = solver_name
    solver[:parameters] = solver_params_vector
    return solver
end

"""
    form_model(data::Dict{Symbol, Arrow.Table}) :: COBRA.LPproblem

Forms an LP problem from the provided data dictionary and returns it as a COBRA.LPproblem.

# Arguments
- `data::Dict{Symbol, Arrow.Table}`: A dictionary containing data tables required to construct the LP problem.
# Returns
- `COBRA.LPproblem`: The constructed LP problem based on the provided data.
# Example
```julia
lpProblem = form_model(data)
```
"""
function form_model(data)
    # Extract and convert the data
    println("Forming the LP problem from the provided data...")
    S_data = data[:S]
    b = Vector{Float64}(data[:b])
    c = Vector{Float64}(data[:c])
    lb = Vector{Float64}(data[:lb])
    ub = Vector{Float64}(data[:ub])
    csense_strs = Vector{String}(data[:csense])
    osense_str = data[:osense]  # e.g. "max"
    osense = osense_str == "max" ? -1 : 1  # 1 for min which is JuMP default, -1 for max
    solver_table = data[:solver][:solver]


    row = Vector{Int64}(S_data[:row])
    col = Vector{Int64}(S_data[:col])
    data = Vector{Float64}(S_data[:data])
    nrow = maximum(row) + 1
    ncol = maximum(col) + 1

    # sense_map = Dict("E" => '=', "G" => '≥', "L" => '≤')
    sense_map = Dict("E" => '=', "G" => '>', "L" => '<')
    csense = [sense_map[c] for c in csense_strs]

    S = sparse(row .+ 1, col .+ 1, data, nrow, ncol)

    # c, A, sense, b, l, u, solver
    solver_name = solver_table[:solver_name]
    solver = changeCobraSolver(solver_name)

    return buildlp(c * osense, S, csense, b, lb, ub, solver.handle)
end


"""
    perform_optimization_using_COBRA(lpProblem::COBRA.LPproblem, solverName::String="GLPK", solverParams::Dict{Symbol, Any}=Dict())

Performs optimization on the given lpProblem using COBRA.jl and the specified solver and parameters.

# Arguments
- `lpProblem::COBRA.LPproblem`: The LP problem to be solved.
- `solverName::String="GLPK"`: The name of the solver to use (default is "GLPK").
- `solverParams::Dict{Symbol, Any}=Dict()`: Solver parameters.
# Returns
- `(status::MathOptInterface.TerminationStatusCode, objval::Float64, sol::Vector{Float64})`: The status of the optimization, the objective value, and the solution vector.
# Example
```julia
status, objval, sol = perform_optimization_using_COBRA(lpProblem, "GLPK", Dict())
```
"""
function perform_optimization_using_COBRA(lpProblem, solverName="GLPK", solverParams=Dict())
    # Perform optimization

    # Set the solver according to https://github.com/opencobra/COBRA.jl/blob/master/docs/src/configuration.md
    # pkgDir = joinpath(dirname(pathof(COBRA)), "..")
    # include(pkgDir * "/config/solverCfg.jl")

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
        # 写入内存
        buf = IOBuffer()
        Arrow.write(buf, result)

        # 取出 Arrow IPC byte stream
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
    send_result(client::Sockets.Socket, result_table::DataFrames.DataFrame)

Sends a result table to the client through the specified socket. The function serializes the `result_table` using Arrow IPC format, writes its length as a header, and then sends the serialized data.

# Arguments
- `client::Sockets.Socket`: The client socket through which the result will be sent.
- `result_table::DataFrames.DataFrame`: The result table that will be serialized and sent to the client. This table contains the data to be transmitted.

# Example
```julia
# Assuming `client` is a valid Sockets.Socket and `result_table` is a DataFrame
send_result(client, result_table)
```
"""
# function send_result(client, result_table)
#     result_io = IOBuffer()
#     Arrow.write(result_io, result_table)
#     result_data = take!(result_io)
#     write(client, UInt32(length(result_data)))
#     write(client, result_data)
# end


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

