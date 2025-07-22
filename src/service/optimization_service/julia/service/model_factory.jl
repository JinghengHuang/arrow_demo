"""
The ModelFactory module provides functionality to create optimization models based on the problem type.
It dispatches to specific model modules (e.g., LPModel, QPModel) to build the JuMP model.
"""
module ModelFactory

include("../model/lp_model.jl")
include("../model/qp_model.jl")
using .LPModel
using .QPModel

export create_model

"""
Map of model types to their corresponding modules.
This map is used to dispatch to the correct model module based on the problem type.
"""
const MODEL_MAP = Dict{String,Module}(
    "LP" => LPModel,
    "QP" => QPModel,
)

"""
    create_model(model_type::String, data::Dict)
Creates a JuMP model based on the specified model type and data.

# Arguments
- `model_type::String`: The type of optimization model to create (e.g., "LP", "QP").
- `data::Dict`: A dictionary containing the optimization problem data, including
    coefficients, constraints, bounds, and solver configuration.

# Returns
- `JuMP.Model`: A JuMP model instance configured for the specified problem type.
- `JuMP.Variable`: The decision variables of the model.
- `JuMP.Expression`: The objective function expression of the model.

# Workflow
1. Looks up the model type in `MODEL_MAP`.
2. If the model type is found, calls the `build_jump_model` function from the corresponding module.
3. If the model type is not found, throws an error.

# Example
```julia
data = Dict(
    :A => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :b => [3.0, 4.0],
    :c => [1.0, 2.0],
    :lb => [0.0, 0.0],
    :ub => [10.0, 10.0],
    :osense => "min"
)
model, x, c = create_model("LP", data)
```
"""
function create_model(model_type::String, data::Dict)
    module_ref = get(MODEL_MAP, uppercase(model_type), nothing)
    if module_ref === nothing
        throw(ErrorException("Unsupported model type: $model_type"))
    end
    return module_ref.build_jump_model(data)
end

end # module ModelFactory
