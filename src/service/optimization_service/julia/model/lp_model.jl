"""
LPModel module provides functionality to create and manage linear programming models using JuMP.
It includes functions to build a JuMP model from problem data and to set up the optimization problem.
"""
module LPModel

using SparseArrays
using JuMP
include("../utils/sparse_matrix.jl")

export build_jump_model

"""
    build_jump_model(data::Dict)
Builds a JuMP model for linear programming based on the provided data dictionary.

# Arguments
- `data::Dict`: A dictionary containing the optimization problem data, including:
  - `:A`: Arrow table representing the constraint matrix.
  - `:b`: Right-hand side vector.
  - `:c`: Objective function coefficients.
  - `:lb`: Lower bounds for the decision variables.
  - `:ub`: Upper bounds for the decision variables.
  - `:csense`: Constraint senses (e.g., "E", "G", "L").
  - `:osense`: Objective sense ("min" or "max").

# Returns
- `JuMP.Model`: A JuMP model instance configured for linear programming.
- `JuMP.Variable`: The decision variables of the model.
- `JuMP.Expression`: The objective function expression of the model.

# Workflow
1. Extracts and converts the data from the dictionary.
2. Constructs the constraint matrix `A` using sparse representation.
3. Sets up the JuMP model with the objective function and constraints.

# Example
```julia
data = Dict(
    :A => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :b => [3.0, 4.0],
    :c => [1.0, 2.0],
    :lb => [0.0, 0.0],
    :ub => [10.0, 10.0],
    :csense => ["E", "G"],
    :osense => "min"
)
model, x, c = build_jump_model(data)
```
"""
function build_jump_model(data)
    A_data = data[:A]
    b = Vector{Float64}(data[:b])
    c = Vector{Float64}(data[:c])
    lb = Vector{Float64}(data[:lb])
    ub = Vector{Float64}(data[:ub])
    csense_strs = Vector{String}(data[:csense])
    osense_str = data[:osense]  # e.g. "max"
    osense = osense_str == "max" ? -1 : 1  # 1 for min which is JuMP default, -1 for max

    A = to_sparse(A_data)
    # sense_map = Dict("E" => '=', "G" => '≥', "L" => '≤')
    sense_map = Dict("E" => '=', "G" => '>', "L" => '<')
    csense = [sense_map[c] for c in csense_strs]

    return buildlp(c * osense, A, csense, b, lb, ub)
end


"""
    buildlp(c, A, sense, b, l, u)
Builds a linear programming model using JuMP.

# Arguments
- `c`: Coefficients of the objective function.
- `A`: Constraint matrix in sparse format.
- `sense`: Constraint senses (e.g., '=', '>', '<').
- `b`: Right-hand side vector for the constraints.
- `l`: Lower bounds for the decision variables.
- `u`: Upper bounds for the decision variables.

# Returns
- `JuMP.Model`: The JuMP model instance.
- `JuMP.Variable`: The decision variables of the model.
- `JuMP.Expression`: The objective function expression of the model.

# Workflow
1. Initializes a JuMP model.
2. Defines decision variables with bounds.
3. Sets the objective function to minimize the linear expression.
4. Adds constraints based on the provided matrix and senses.
5. Returns the model, decision variables, and objective coefficients.

# Example
```julia
c = [1.0, 2.0]
A = sparse([1.0, 2.0], [1.0, 2.0], [1.0, 2.0], 2, 2)
sense = ['=', '≥']
b = [3.0, 4.0]
l = [0.0, 0.0]
u = [10.0, 10.0]
model, x, c = buildlp(c, A, sense, b, l, u)
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

end # module LPModel