"""
    SolverConfig

A common solver configuration structure that encapsulates:

- `name`:   Solver name (e.g., "HiGHS", "GLPK", etc.)
- `type`:   Problem type (e.g., "LP", "QP", etc.)
- `params`: Dictionary of solver parameters (Symbol => Any)
- `handle`: Optimizer handle configured with attributes, ready to be passed to `Model(optimizer)`.

# Example

```julia
params = Dict(:presolve => "off", :output_flag => true)
cfg = SolverConfig("HiGHS", "QP", params)
model = Model(cfg.handle)
````
"""

"""
const SOLVER_MAP

A dictionary mapping upper-case solver names (e.g., "HIGHS") to constructor functions
that return a JuMP-compatible Optimizer.

You can extend this with more solvers such as "MOSEK", etc.

Supported Solvers: "HIGHS", "GLPK", "GUROBI", "IPOPT", "CSDP", "HYPATIA", "MOSEK"
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

mutable struct SolverConfig
    name::String
    type::String
    params::Dict{Symbol,Any}
    handle::Any

    """
        SolverConfig(name::String, type::String, params::Dict{Symbol,Any})

    Constructor for SolverConfig.

    Automatically constructs an optimizer handle using the solver name
    and parameters, ready to be used in JuMP `Model`.

    # Arguments
    - `name`: Solver name (e.g., "HiGHS", "GUROBI")
    - `type`: Problem type (e.g., "QP", "LP")
    - `params`: Dictionary of raw solver parameters (`Symbol => Any`)

    # Returns
    - A `SolverConfig` instance with a fully constructed optimizer handle.
    """
    function SolverConfig(name::String, type::String, params::Dict{Symbol,<:Any})
        handle = changeSolver(name)
        attrs = [MOI.RawOptimizerAttribute(string(k)) => v for (k, v) in params]
        optimizer = optimizer_with_attributes(handle, attrs...)
        new(name, type, params, optimizer)
    end


    """
    changeSolver(name::AbstractString; printLevel::Int = 1) -> Optimizer

    Returns the optimizer constructor for the given solver name. Throws an error if
    the solver is not supported.

    # Arguments
    name: Solver name (case-insensitive), e.g. "HiGHS", "Gurobi"

    printLevel: (optional) Verbosity level, currently unused

    # Returns
    Optimizer constructor usable by optimizer_with_attributes

    # Errors
    Throws an error if the solver is not registered in SOLVER_MAP

    # Example
    ```julia
    opt = changeSolver("HiGHS")
    ````
    """
    function changeSolver(name::AbstractString; printLevel::Int=1)
        println("Changing solver to: $name with print level: $printLevel")

        name_upper = uppercase(name)

        if haskey(SOLVER_MAP, name_upper)
            try
                return SOLVER_MAP[name_upper]()  # 调用构造器返回 Optimizer 类型
            catch e
                error("Failed to set solver `$name_upper`: $(e)")
            end
        else
            error("Solver `$name_upper` is not supported. Please choose from: $(keys(SOLVER_MAP))")
        end
    end


end