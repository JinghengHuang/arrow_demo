"""
IOUtils module for reading and writing Arrow IPC data over TCP sockets.
Provides functions to read optimization data from a client and send results back.
"""
module IOUtils

using Arrow
using DataFrames
using Sockets

export read_data_from_client, send_success_result, send_failure_result


"""
    read_data_from_client(client::TCPSocket) -> Dict{Symbol, Any}
Reads optimization data from a client socket and returns it as a dictionary.

# Arguments
- `client::TCPSocket`: The socket connection to the client.

# Returns
- `Dict{Symbol, Any}`: A dictionary containing the optimization data, where keys are
    symbols corresponding to the column names in the Arrow table.

# Workflow
1. Reads a 4-byte header indicating the length of the incoming data.
2. Reads the specified number of bytes from the client.
3. Constructs an `IOBuffer` from the received data.
4. Reads the Arrow table from the buffer.
5. Converts the Arrow table to a dictionary, where each key corresponds to a column name.

# Example
```julia
client = connect("127.0.0.1", 65432)
data_dict = read_data_from_client(client)
```
"""
function read_data_from_client(client::TCPSocket)
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
Sends a success result back to the client as Arrow IPC bytes.

# Arguments
- `client::TCPSocket`: The socket connection to the client.
- `status`: The termination status of the optimization (e.g., `:OPTIMAL`).
- `objval::Float64`: The value of the objective function after optimization.
- `sol::Vector{Float64}`: The optimized variable values as a vector.

# Format
- Constructs a `DataFrame` with:
    - `success::Bool = true`
    - `status::String`: The termination status as a string.
    - `obj_val::Float64`: The objective value.
    - `solution::Vector{Float64}`: The solution vector.

# Returns
- Nothing. Sends the data to the client with a 4-byte header followed by Arrow IPC payload.
"""
function send_success_result(client::TCPSocket, status, objval::Float64, sol::Vector{Float64})
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

Sends an error message back to the client as Arrow IPC bytes.

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
function send_failure_result(client::TCPSocket, error::Exception)
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

end # module IOUtils