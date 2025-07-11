module QPModel

include("solver_config.jl")

using JuMP
using HiGHS
using SparseArrays
using LinearAlgebra

# -------------------------------------------------------------------------------------------
"""
    QPproblem(Q, c, A, b, G, h, lb, ub, osense)

General type for storing a QP problem which contains the following fields:

- `Q`:      Quadratic coefficient matrix (n x n)
- `c`:      Linear coefficient vector (n x 1)
- `A`:      Equality constraint matrix (meq x n)
- `b`:      Equality RHS vector (meq x 1)
- `G`:      Inequality constraint matrix (mineq x n)
- `h`:      Inequality RHS vector (mineq x 1)
- `lb`:     Lower bound vector
- `ub`:     Upper bound vector
- `osense`: Objective sense (-1 for max, 1 for min)
"""
mutable struct QPproblem
    Q::SparseMatrixCSC{Float64,Int64}
    c::Vector{Float64}
    A::SparseMatrixCSC{Float64,Int64}
    b::Vector{Float64}
    G::SparseMatrixCSC{Float64,Int64}
    h::Vector{Float64}
    lb::Vector{Float64}
    ub::Vector{Float64}
    osense::Int8
end


"""
    build_jump_model(data)

Build QP model from Arrow-compatible `data` dictionary.
"""
function build_jump_model(data)
    # Extract fields
    Q_data = data[:Q]

    c = Vector{Float64}(data[:c])
    A_data = data[:A]
    b = Vector{Float64}(data[:b])
    G_data = data[:G]
    h = Vector{Float64}(data[:h])
    lb = Vector{Float64}(data[:lb])
    ub = Vector{Float64}(data[:ub])
    osense_str = data[:osense]
    osense = osense_str == "max" ? -1 : 1

    solver_name = data[:solver][:solver_name]
    solver = changeSolver(solver_name)

    # Construct sparse matrices
    function to_sparse(mat)
        row = Vector{Int64}(mat[:row]) .+ 1
        col = Vector{Int64}(mat[:col]) .+ 1
        val = Vector{Float64}(mat[:val])
        nrow = maximum(row)
        ncol = maximum(col)
        sparse(row, col, val, nrow, ncol)
    end

    Q = to_sparse(Q_data)
    A = to_sparse(A_data)
    G = to_sparse(G_data)

    # Build model
    return buildqp(Q * osense, c * osense, A, b, G, h, lb, ub, solver.handle)
end


"""
    buildqp(Q, c, A, b, G, h, lb, ub, solver)

Build a JuMP QP model.

Returns:
- model: JuMP.Model
- x: JuMP.VariableRef
- Q, c: Stored for later use
"""
function buildqp(Q, c, A, b, G, h, lb, ub, solver)
    n = length(c)
    model = Model(solver)

    @variable(model, lb[i] <= x[i=1:n] <= ub[i])

    @objective(model, Min, 0.5 * dot(x, Q * x) + dot(c, x))

    if size(A, 1) > 0
        @constraint(model, A * x .== b)
    end

    if size(G, 1) > 0
        @constraint(model, G * x .<= h)
    end
    return model, x, Q, c
end

end
