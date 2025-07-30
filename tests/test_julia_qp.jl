include("../src/service/optimization_service/julia/service/optimization_service.jl")
import Pkg;
Pkg.add("JSON");
using JSON

# how to use
# in project root directory, run:
# julia --project=src/service/optimization_service/julia tests/test_julia_qp.jl

# read from json and return julia dictionary, no use of Arrow
function read_json_to_dict(file_path::String)

    open(file_path) do file
        data_dicts = []
        json_data = JSON.parse(file)
        model_data = json_data["model_data"]
        solver_data_arrays = json_data["solvers"]
        for solver_data in solver_data_arrays
            solver_data = Dict(Symbol(k) => v for (k, v) in solver_data)
            data_dict = Dict(
                :solver => solver_data,  # Assuming the first solver is used
                :Q => Dict(Symbol(k) => v for (k, v) in model_data["Q"]),
                :c => model_data["c"],
                :A => Dict(Symbol(k) => v for (k, v) in model_data["A"]),
                :b => model_data["b"],
                :G => Dict(Symbol(k) => v for (k, v) in model_data["G"]),
                :h => model_data["h"],
                :lb => model_data["lb"],
                :ub => model_data["ub"],
                :osense => model_data["osense"],
            )
            push!(data_dicts, data_dict)
        end
        return data_dicts
    end
end

data_dicts = read_json_to_dict("tests/ipc_http_test/qp.json")
for data in data_dicts
    solver_name = uppercase(data[:solver][:solver_name])
    solver_params = get(data[:solver], :solver_params, Dict())
    if solver_name in ["GUROBI", "MOSEK"]
        try
            termination_status, objective_value, solution = OptimizationService.optimize(data)
        catch e
            @assert occursin("license", lowercase(string(e))) "Expected 'license' in error message, but got: $(e)"
        end
    elseif solver_name == "GLPK"
        try
            termination_status, objective_value, solution = OptimizationService.optimize(data)
        catch e
            @assert occursin("UnsupportedAttribute", string(e)) "got: $(e)"
        end
    elseif solver_name == "HIGHS" && !isempty(solver_params)
        try
            termination_status, objective_value, solution = OptimizationService.optimize(data)
        catch e
            @assert occursin("MathOptInterface.SetAttributeNotAllowed", string(e)) "got: $(e)"
        end
    else
        termination_status, objective_value, solution = OptimizationService.optimize(data)
        println("=========Objective Value: $objective_value for solver $solver_name")
        @assert length(solution) == length(data[:c]) "Solution length mismatch: expected $(length(data[:c])), got $(length(solution))"
    end
end