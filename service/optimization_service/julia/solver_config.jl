
"""
    SolverConfig(name, handle)

Definition of a common solver type, which inclues the name of the solver and other parameters

- `name`:           Name of the solver (alias)
- `handle`:         Solver handle used to refer to the solver

"""

mutable struct SolverConfig
    name::String
    handle
end


#-------------------------------------------------------------------------------------------
"""
    changeSolver(name, params, printLevel)

Function used to change the solver and include the respective solver interfaces

# INPUT

- `name`:           Name of the solver (alias)

# OPTIONAL INPUT

- `params`:         Solver parameters as a row vector with tuples
- `printLevel`:     Verbose level (default: 1). Mute all output with `printLevel = 0`.

# OUTPUT

- `solver`:         Solver object with a `handle` field

# EXAMPLES

Minimum working example (for the CPLEX solver)
```julia
julia> changeCobraSolver("CPLEX", cpxControl)
```

Minimum working example (for the GLPK solver)
```julia
julia> solverName = :GLPK
julia> solver = changeCobraSolver(solverName)
```

"""

function changeSolver(name, params=[]; printLevel::Int=1)
    # convert type of name
    if typeof(name) != :String
        name = string(name)
    end

    # Convert the input name to uppercase for case-insensitive matching
    name = uppercase(name)

    # define empty solver object
    solver = SolverConfig(name, 0)

    # define the solver handle
    if name == "CPLEX"
        try
            if abs(printLevel) > 1
                printLevel = 1
            end
            solver.handle = CPLEX.Optimizer
        catch
            error("The solver `CPLEX` cannot be set using `changeCobraSolver()`.")
        end

    elseif name == "GLPK"
        try
            if length(params) > 1
                solver.handle = GLPK.Optimizer
            else
                solver.handle = GLPK.Optimizer
            end
        catch
            error("The solver `GLPK` cannot be set using `changeCobraSolver()`.")
        end

    elseif name == "GUROBI"
        try
            # define default parameters
            if isempty(params)
                push!(params, -1) # default (ref: http://www.gurobi.com/documentation/8.0/refman/method.html#parameter:Method)
                push!(params, 1) # default (ref: http://www.gurobi.com/documentation/8.0/refman/outputflag.html)
            end

            # set the output flag depending on the printLevel
            if printLevel != 1
                params[2] = printLevel
            end

            # define the solver handle
            solver.handle = Gurobi.Optimizer
            # solver.handle = GurobiSolver(Method=params[1], OutputFlag=params[2])
        catch e
            rethrow(e)
            # error("The solver `Gurobi` cannot be set using `changeCobraSolver()`.")
        end
    elseif name == "HIGHS"
        try
            if length(params) > 1
                solver.handle = HiGHS.Optimizer
            else
                solver.handle = HiGHS.Optimizer
            end
        catch
            error("The solver `HiGHS` cannot be set using `changeCobraSolver()`.")
        end
        #=
        elseif name == "Clp"
            try
                solver.handle = ClpSolver()
            catch
                error("The solver `Clp` cannot be set using `changeCobraSolver()`.")
            end

        elseif name == "Mosek"
            try
                if printLevel == 1
                    printLevel = 10 # default value: https://docs.mosek.com/7.1/toolbox/MSK_IPAR_LOG.html
                end
                solver.handle = MosekSolver(MSK_IPAR_LOG=printLevel)
            catch
              error("The solver `Mosek` cannot be set using `changeCobraSolver()`.")
            end
        =#
    else
        solver.handle = -1
        error("The solver is not supported. Please set the solver name to one the supported solvers.")
    end

    return solver

end
