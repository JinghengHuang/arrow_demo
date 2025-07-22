"""
QPModel module for building and solving Quadratic Programming (QP) problems using JuMP.
This module provides functionality to create a QP model from a dictionary of data,
including quadratic coefficients, linear coefficients, constraints, and bounds.
It supports both equality and inequality constraints and allows for setting the objective sense (minimization or maximization).
"""
module QPModel

using SparseArrays
using LinearAlgebra
using JuMP
include("../utils/sparse_matrix.jl")

export build_jump_model

"""
    build_jump_model(data::Dict{Symbol,Any})
Builds a JuMP model for quadratic programming based on the provided data dictionary.

# Arguments
- `data::Dict{Symbol,Any}`: A dictionary containing the model parameters.

# Fields in `data`:
- `:Q`: Arrow Table with keys `:row`, `:col`, `:val` for the quadratic coefficients.
- `:c`: Vector of linear coefficients.
- `:A`: Arrow Table with keys `:row`, `:col`, `:val` for the equality constraints.
- `:b`: Vector for the right-hand side of the equality constraints.
- `:G`: Arrow Table with keys `:row`, `:col`, `:val` for the inequality constraints (optional).
- `:h`: Vector for the right-hand side of the inequality constraints (optional).
- `:lb`: Vector for the lower bounds of the decision variables.
- `:ub`: Vector for the upper bounds of the decision variables.
- `:osense`: Objective sense as a string ("max" or "min").

# Returns
- `JuMP.Model`: A JuMP model instance configured for quadratic programming.
- `JuMP.Variable`: The decision variables of the model.
- `JuMP.Expression`: The objective function expression of the model.

# Workflow
1. Extracts the quadratic coefficients, linear coefficients, constraints, and bounds from the `data` dictionary.
2. Converts the Arrow Tables to sparse matrices using the `to_sparse` function.
3. Constructs the JuMP model with the objective function and constraints.
4. Returns the model, decision variables, and objective coefficients.

# Example
```julia
data = Dict(
    :Q => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :c => [1.0, 2.0],
    :A => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :b => [3.0, 4.0],
    :G => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :h => [5.0, 6.0],
    :lb => [0.0, 0.0],
    :ub => [10.0, 10.0],
    :osense => "max"
)
model, x, Q, c = build_jump_model(data)
```
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

    Q = to_sparse(Q_data)
    A = to_sparse(A_data)
    G = to_sparse(G_data)

    # Build model
    return buildqp(Q * osense, c * osense, A, b, G, h, lb, ub)
end


"""
    buildqp(Q, c, A, b, G, h, lb, ub)
Builds a quadratic programming model using JuMP.

# Arguments
- `Q`: Quadratic coefficients matrix.
- `c`: Linear coefficients vector.
- `A`: Constraint matrix for equality constraints.
- `b`: Right-hand side vector for equality constraints.
- `G`: Constraint matrix for inequality constraints.
- `h`: Right-hand side vector for inequality constraints.
- `lb`: Lower bounds for the decision variables.
- `ub`: Upper bounds for the decision variables.

# Returns
- `JuMP.Model`: A JuMP model instance configured for quadratic programming.
- `JuMP.Variable`: The decision variables of the model.
- `JuMP.Expression`: The objective function expression of the model.

# Workflow
1. Initializes a JuMP model.
2. Defines decision variables with bounds.
3. Sets the objective function to minimize the quadratic expression.
4. Adds equality constraints based on the provided matrix.
5. Adds inequality constraints based on the provided matrix.
6. Returns the model, decision variables, and objective coefficients.

# Example
```julia
Q = sparse([1.0, 2.0], [1.0, 2.0], [1.0, 2.0], 2, 2)
c = [1.0, 2.0]
A = sparse([1.0, 2.0], [1.0, 2.0], [1.0, 2.0], 2, 2)
b = [3.0, 4.0]
G = sparse([1.0, 2.0], [1.0, 2.0], [1.0, 2.0], 2, 2)
h = [5.0, 6.0]
lb = [0.0, 0.0]
ub = [10.0, 10.0]
model, x, Q, c = buildqp(Q, c, A, b, G, h, lb, ub)
```
"""
function buildqp(Q, c, A, b, G, h, lb, ub)
    n = length(c)
    model = Model()

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

end # module QPModel
