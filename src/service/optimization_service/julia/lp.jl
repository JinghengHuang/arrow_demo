module LPModel
include("solver_config.jl")

using JuMP
using HiGHS
using SparseArrays
#-------------------------------------------------------------------------------------------
"""
    LPproblem(S, b, c, lb, ub, osense, csense)

General type for storing an LP problem which contains the following fields:

- `S`:              LHS matrix (m x n)
- `b`:              RHS vector (m x 1)
- `c`:              Objective coefficient vector (n x 1)
- `lb`:             Lower bound vector (n x 1)
- `ub`:             Upper bound vector (n x 1)
- `osense`:         Objective sense (scalar; -1 ~ "max", +1 ~ "min")
- `csense`:         Constraint senses (m x 1, 'E' or '=', 'G' or '>', 'L' ~ '<')
- `solver`:         A `::SolverConfig` object that contains a valid `handle` to the solver

"""

mutable struct LPproblem
    S::Union{SparseMatrixCSC{Float64,Int64},AbstractMatrix}
    b::Array{Float64,1}
    c::Array{Float64,1}
    lb::Array{Float64,1}
    ub::Array{Float64,1}
    osense::Int8
    csense::Array{Char,1}
end





function build_jump_model(data)
    # println("Data received: ", data)
    # Convert the input sense to a vector of characters
    # Extract and convert the data
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
    solver = changeSolver(solver_name)

    # Create the LPproblem object
    return buildlp(c * osense, S, csense, b, lb, ub, solver.handle)
end




#-------------------------------------------------------------------------------------------
"""
    buildlp(c, A, sense, b, l, u, solver)

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
julia> model, x, c = buildlp(c, A, sense, b, l, u, solver)
```

"""

function buildlp(c, A, sense, b, l, u, solver)
    N = length(c)
    model = Model(solver)
    x = @variable(model, l[i] <= x[i=1:N] <= u[i])
    @objective(model, Min, c' * x)
    eq_rows, ge_rows, le_rows = sense .== '=', sense .== '>', sense .== '<'
    @constraint(model, A[eq_rows, :] * x .== b[eq_rows])
    @constraint(model, A[ge_rows, :] * x .>= b[ge_rows])
    @constraint(model, A[le_rows, :] * x .<= b[le_rows])
    return model, x, c
end



end