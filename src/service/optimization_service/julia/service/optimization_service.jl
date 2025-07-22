
"""
OptimizationService module provides the functionality to perform optimization tasks.
"""
module OptimizationService
using JuMP
include("solver_factory.jl")
include("model_factory.jl")

export optimize

"""
    optimize(data_dict::Dict)
Performs optimization based on the provided data dictionary.
# Arguments
- `data_dict::Dict`: A dictionary containing the optimization problem data and solver configuration.

# Returns
- `termination_status`: The status of the optimization (e.g., `:OPTIMAL`, `:INFEASIBLE`).
- `objective_value`: The value of the objective function after optimization.
- `solution`: The optimized variable values as a vector.

# Workflow
1. Extracts the solver configuration and problem type from the data dictionary.
2. Creates a solver instance using `SolverFactory.create_solver`.
3. Dispatches to the appropriate model module using `ModelFactory.create_model`.
4. Sets the optimizer for the model.
5. Calls `optimize!` to solve the optimization problem.
6. Returns the termination status, objective value, and solution vector.

# Example
```julia
data_dict = Dict(
    :solver => Dict(:solver_type => "LP", :options => Dict()),
    :c => [1.0, 2.0],
    :A => Arrow.Table(row=[0, 1], col=[0, 1], val=[1.0, 2.0]),
    :b => [3.0, 4.0],
    :lb => [0.0, 0.0],
    :ub => [10.0, 10.0],
    :osense => "min"
)
termination_status, objective_value, solution = optimize(data_dict)
```
"""
function optimize(data_dict)
    solver_table = data_dict[:solver]
    problem_type = solver_table[:solver_type]
    optimizer = SolverFactory.create_solver(solver_table)
    model, x, c = ModelFactory.create_model(problem_type, data_dict)
    set_optimizer(model, optimizer)
    # send success result to client
    start_time = time()
    optimize!(model)
    end_time = time()
    @info "Time taken to solve the $(problem_type) problem: $(end_time - start_time) seconds."
    return termination_status(model), objective_value(model), value.(x)
end

end # module OptimizationService