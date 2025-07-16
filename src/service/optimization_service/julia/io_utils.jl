"""
# IOUtils.jl
# Utility functions for reading and writing data in the optimization server
# This module provides functions to read Arrow IPC data from a client and send results back.
# It handles serialization and deserialization of optimization results in Arrow format.
"""
module IOUtils

using Arrow
using DataFrames
using Sockets

export read_data_from_client, send_success_result, send_failure_result


"""
    read_data_from_client(client::TCPSocket) -> Dict{Symbol, Any}

Reads Arrow IPC data sent from a TCP client and deserializes it into a dictionary.

# Arguments
- `client::TCPSocket`: The socket representing the client connection.

# Returns
- `Dict{Symbol, Any}`: A dictionary mapping table field names (symbols) to their first element values. 
  Typically used to extract model and solver parameters.

# Notes
- The data must be sent as a binary stream with a 4-byte length header followed by Arrow IPC bytes.
- Assumes the Arrow Table has singleton arrays for each key (i.e., single-row metadata).
"""
function read_data_from_client(client)
    tables = Dict{Symbol,Any}()
    header = read(client, UInt32)
    data_length = Int(header)
    data = read(client, data_length)

    buf = IOBuffer(data)
    table = Arrow.Table(buf)

    for key in keys(table)
        tables[key] = table[key][1]
    end
    return tables
end

"""
    send_success_result(client::TCPSocket, status, objval::Float64, sol::Vector{Float64}) -> Nothing

Sends a successful optimization result as an Arrow Table to the client.

# Arguments
- `client::TCPSocket`: The socket connection to the client.
- `status`: Optimization termination status (typically from `JuMP.termination_status(model)`).
- `objval::Float64`: The final objective value of the optimized problem.
- `sol::Vector{Float64}`: The optimal solution vector.

# Format
- Constructs a `DataFrame` with fields:
    - `success::Bool = true`
    - `status::String`
    - `objective_value::Float64`
    - `solution::Vector{Float64}` (wrapped in an array to preserve as single row)

- Serializes the dataframe into Arrow IPC binary and sends:
    - a 4-byte length header (UInt32)
    - followed by the Arrow data stream

# Returns
- Nothing. Data is streamed to the client socket.
"""
function send_success_result(client, status, objval, sol)
    df = DataFrame(
        success=true,
        status=string(status),
        obj_val=objval,
        solution=[sol],
    )
    buf = IOBuffer()
    Arrow.write(buf, df)
    ipc_bytes = take!(buf)

    write(client, UInt32(length(ipc_bytes)))
    write(client, ipc_bytes)
end

"""
    send_failure_result(client::TCPSocket, error::Exception) -> Nothing

Sends an error message back to the client as a structured Arrow Table.

# Arguments
- `client::TCPSocket`: The socket connection to the client.
- `error::Exception`: The caught exception or error to report.

# Format
- Constructs a `DataFrame` with:
    - `success::Bool = false`
    - `error_message::String`: Captures exception message via `string(error)`

# Returns
- Nothing. Sends the data to the client with a 4-byte header followed by Arrow IPC payload.
"""
function send_failure_result(client, error)
    df = DataFrame(
        success=false,
        error_message=string(error)
    )
    buf = IOBuffer()
    Arrow.write(buf, df)
    ipc_bytes = take!(buf)

    write(client, UInt32(length(ipc_bytes)))
    write(client, ipc_bytes)
end

end # module
