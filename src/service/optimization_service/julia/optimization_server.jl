module OptimizationServer

# === Core Packages ===
using JuMP
using HiGHS, Ipopt, CSDP, GLPK, Hypatia, Gurobi, MosekTools, Mosek
using Sockets
using SparseArrays

# === Internal Modules ===
include("solver_config.jl")
include("io_utils.jl")
include("registry.jl")
include("lp.jl")
include("qp.jl")

using .IOUtils
using .Registry

# Export the functions
export start_server

# === Register Available Problem Builders ===
Registry.register_model("LP", (data) -> LPModel.build_jump_model(data))
Registry.register_model("QP", (data) -> QPModel.build_jump_model(data))

# ------------------------------------------------------------------------------
# Server Entry Point
# ------------------------------------------------------------------------------

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
    println("Listening on $host:$port")

    while true
        client = accept(server)
        client_ip, client_port = getpeername(client)
        println("Accepted client connection from address: $client_ip: $client_port")
        @async handle_optimization_request(client)
    end
end

#------------------------------------------------------------------------------
# Request Handler
# ------------------------------------------------------------------------------

"""
    handle_optimization_request(client::TCPSocket)

Handles optimization requests from the given client. Processes the received data to form an LP problem,
runs optimization using COBRA.jl, and sends results back to the client.

# Workflow
1. Reads Arrow IPC input data via TCP.
2. Parses solver and problem metadata.
3. Builds a JuMP model using the appropriate problem type (e.g., LP or QP).
4. Applies solver configuration and runs optimize!.
5. Sends result (success or failure) back to client in Arrow format.

# Arguments
- `client::TCPSocket`: The client socket connected to the server.

# Example
```julia
handle_optimization_request(optimization_client)

```
# Note
Automatically closes the client socket after processing.
"""
function handle_optimization_request(client)
    try
        data_dict = read_data_from_client(client)
        optimizer = get_optimizer(data_dict)
        builder = Registry.get_builder(uppercase(optimizer.type))
        if builder === nothing
            error("Problem type $problem_type not supported by the server.")
        end
        model, x, c = builder(data_dict)
        set_optimizer(model, optimizer.handle)
        # send success result to client
        start_time = time()
        status, objval, sol = solve(model, x)
        end_time = time()
        @info "Time taken to solve the $(optimizer.type) problem in COBRA.jl: $(end_time - start_time) seconds."
        send_success_result(client, status, objval, sol)
    catch e
        @error "Error handling optimization request: $(e)"
        send_failure_result(client, e)
    finally
        close(client)
    end
end


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
"""
get_optimizer(data::Dict) -> SolverConfig

Extracts solver configuration from client input and returns a SolverConfig object.

Arguments
data::Dict{Symbol, Any}: Parsed data from the Arrow Table, containing keys like :solver.

Returns
SolverConfig: Struct containing solver name, type, parameter dict, and instantiated optimizer.
"""
function get_optimizer(data)
    solver_table = data[:solver]
    solver_name = solver_table[:solver_name]
    problem_type = solver_table[:solver_type]
    solver_params = solver_table[:params]
    # Convert NamedTuple to Dict with Symbol keys
    params_dict = Dict(pairs(solver_params))
    optimizer = SolverConfig(solver_name, problem_type, params_dict)
    return optimizer
end

"""
solve(model::Model, x) -> NamedTuple

Executes optimize! on the given model and extracts results.

# Arguments
model::Model: A JuMP model that has already been populated and configured.

x: The decision variable vector (used to extract solution values).

# Returns
NamedTuple:
status: Termination status from JuMP.
objval: Objective value.
sol: Vector of variable values.
"""
function solve(model, x)
    optimize!(model)
    return (
        status=termination_status(model),
        objval=objective_value(model),
        sol=value.(x)
    )
end



end  # module

