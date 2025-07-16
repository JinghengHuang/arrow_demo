"""
# LPModel.jl
# Linear Programming Model Representation using JuMP
# This module provides functions to build and manipulate linear programming models using JuMP.
"""
module LPModel

using SparseArrays
using JuMP
#-------------------------------------------------------------------------------------------
"""
    LPproblem(A, b, c, lb, ub, osense, csense)

General type for storing an LP problem which contains the following fields:

- `A`:              LHS matrix (m x n)
- `b`:              RHS vector (m x 1)
- `c`:              Objective coefficient vector (n x 1)
- `lb`:             Lower bound vector (n x 1)
- `ub`:             Upper bound vector (n x 1)
- `osense`:         Objective sense (scalar; -1 ~ "max", +1 ~ "min")
- `csense`:         Constraint senses (m x 1, 'E' or '=', 'G' or '>', 'L' ~ '<')
- `solver`:         A `::SolverConfig` object that contains a valid `handle` to the solver

"""

mutable struct LPproblem
    A::Union{SparseMatrixCSC{Float64,Int64},AbstractMatrix}
    b::Array{Float64,1}
    c::Array{Float64,1}
    lb::Array{Float64,1}
    ub::Array{Float64,1}
    osense::Int8
    csense::Array{Char,1}
end




"""
    build_jump_model(data::Dict{Symbol,Any}) -> LPproblem
Builds a JuMP model from the provided data dictionary.
# Arguments
- `data::Dict{Symbol,Any}`: A dictionary containing the model parameters.
# Returns
- `LPproblem`: An instance of `LPproblem` containing the model data.
# Notes
- The dictionary should contain the following keys:
  - `:A`: Arrow Table with keys `:row`, `:col`, `:val` for the sparse matrix.
  - `:b`: Right-hand side vector.
  - `:c`: Objective coefficient vector.
  - `:lb`: Lower bounds vector.
  - `:ub`: Upper bounds vector.
  - `:csense`: Constraint senses as an array of strings (e.g., "E", "G", "L").
  - `:osense`: Objective sense as a string  (e.g., "max" or "min").
# Example
```julia
data = Dict(
    :A => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :b => [3.0, 4.0],
    :c => [1.0, 2.0],
    :lb => [0.0, 0.0],
    :ub => [10.0, 10.0],
    :csense => ["E", "G"],
    :osense => "max"
)
model = build_jump_model(data)
```
"""
function build_jump_model(data)
    # Extract and convert the data
    A_data = data[:A]
    b = Vector{Float64}(data[:b])
    c = Vector{Float64}(data[:c])
    lb = Vector{Float64}(data[:lb])
    ub = Vector{Float64}(data[:ub])
    csense_strs = Vector{String}(data[:csense])
    osense_str = data[:osense]  # e.g. "max"
    osense = osense_str == "max" ? -1 : 1  # 1 for min which is JuMP default, -1 for max
    # solver_table = data[:solver]

    row = Vector{Int64}(A_data[:row])
    col = Vector{Int64}(A_data[:col])
    val = Vector{Float64}(A_data[:val])
    nrow = maximum(row) + 1
    ncol = maximum(col) + 1

    # sense_map = Dict("E" => '=', "G" => '≥', "L" => '≤')
    sense_map = Dict("E" => '=', "G" => '>', "L" => '<')
    csense = [sense_map[c] for c in csense_strs]

    A = sparse(row .+ 1, col .+ 1, val, nrow, ncol)

    # Create the LPproblem object
    return buildlp(c * osense, A, csense, b, lb, ub)
end




#-------------------------------------------------------------------------------------------
"""
    buildlp(c, A, sense, b, l, u)

Function used to build a model using JuMP.

# INPUTS

- `c`:           The objective vector, always in the sense of minimization
- `A`:           Constraint matrix
- `sense`:       Vector of constraint sense characters '<', '=', and '>'
- `b`:           Right-hand side vector
- `l`:           Vector of lower bounds on the variables
- `u`:           Vector of upper bounds on the variables
- `solver`:      A `::SolverConfig` object that contains a valid `handle`to the solver

# OUTPUTS

- `model`:       An `::LPproblem` object that has been built using the JuMP.
- `x`:           Primal solution vector
- `c`:           The objective vector, always in the sense of minimization

# EXAMPLES

```julia
julia> model, x, c = buildlp(c, A, sense, b, l, u)
```

"""

function buildlp(c, A, sense, b, l, u)
    N = length(c)
    model = Model()
    x = @variable(model, l[i] <= x[i=1:N] <= u[i])
    @objective(model, Min, c' * x)
    eq_rows, ge_rows, le_rows = sense .== '=', sense .== '>', sense .== '<'
    @constraint(model, A[eq_rows, :] * x .== b[eq_rows])
    @constraint(model, A[ge_rows, :] * x .>= b[ge_rows])
    @constraint(model, A[le_rows, :] * x .<= b[le_rows])
    return model, x, c
end



end