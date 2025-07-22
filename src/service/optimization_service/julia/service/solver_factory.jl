
"""
SolverFactory module provides functionality to create and configure solvers for optimization problems.
"""
module SolverFactory
using JuMP
using HiGHS, Ipopt, CSDP, GLPK, Hypatia, Gurobi, MosekTools, Mosek

export create_solver

"""
Map of solver names to their constructors.
"""
const SOLVER_MAP = Dict(
    "GLPK" => () -> GLPK.Optimizer,
    "GUROBI" => () -> Gurobi.Optimizer,
    "HIGHS" => () -> HiGHS.Optimizer,
    "IPOPT" => () -> Ipopt.Optimizer,
    "CSDP" => () -> CSDP.Optimizer,
    "HYPATIA" => () -> Hypatia.Optimizer,
    "MOSEK" => () -> Mosek.Optimizer,
)


"""
create_solver(solver_table::Dict)
Creates a JuMP optimizer based on the provided solver configuration.

# Arguments
- `solver_table::Dict`: A dictionary containing the solver name and parameters.

# Returns
- `JuMP.Optimizer`: An instance of the JuMP optimizer configured with the specified solver.

# Example
```julia
solver_table = Dict(
    :solver_name => "GLPK",
    :params => Dict(:msg_lev => "GLP_MSG_ALL")
)
optimizer = create_solver(solver_table)
```

# Notes
- The `solver_table` should contain:
  - `:solver_name`: A string indicating the solver type (e.g., "GLPK", "GUROBI").
  - `:params`: A dictionary of parameters specific to the solver.
- The function converts the parameters to a format compatible with JuMP's optimizer attributes.

# Throws
- `KeyError` if the solver name is not found in `SOLVER_MAP`.
- `ErrorException` if the solver parameters are invalid or cannot be applied.

"""
function create_solver(solver_table)
    solver_name = solver_table[:solver_name]
    solver_params = solver_table[:params]
    # Convert NamedTuple to Dict with Symbol keys
    params_dict = Dict(pairs(solver_params))

    optimizer_constructor = SOLVER_MAP[uppercase(solver_name)]()
    attrs = [MOI.RawOptimizerAttribute(string(k)) => v for (k, v) in params_dict]
    optimizer = optimizer_with_attributes(optimizer_constructor, attrs...)
    @info "Created solver: $solver_name with parameters: $params_dict"
    return optimizer
end


end  # module SolverFactory
