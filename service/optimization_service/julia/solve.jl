#-------------------------------------------------------------------------------------------
#=
    Compared to this file in Cobra.jl, only changeCobraSolver was modified to include the Gurobi solver.
=#

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
"""
    LPproblem(S, b, c, lb, ub, osense, csense, rxns, mets)

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
    # rxns::Array{String,1}
    # mets::Array{String,1}
end


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
    try
        N = length(c)
        model = Model(solver)
        x = @variable(model, l[i] <= x[i=1:N] <= u[i])
        @objective(model, Min, c' * x)
        eq_rows, ge_rows, le_rows = sense .== '=', sense .== '>', sense .== '<'
        @constraint(model, A[eq_rows, :] * x .== b[eq_rows])
        @constraint(model, A[ge_rows, :] * x .>= b[ge_rows])
        @constraint(model, A[le_rows, :] * x .<= b[le_rows])
        return model, x, c
    catch e
        rethrow(e)
        # printout error e details
        println("Error building LP model with JuMP: ", e)

    end
end

#-------------------------------------------------------------------------------------------
"""
    solvelp(model, x)

Function used to solve a LPproblem using JuMP.

# INPUTS

- `model`:       An `::LPproblem` object that has been built using the JuMP.
- `x`:           Primal solution vector

# OUTPUTS

- `status`:      Termination status
- `objval`:      Optimal objective value
- `sol`:         Primal solution vector

# EXAMPLES

```julia
julia> status, objval, sol = solvelp(model, x)
```

"""

function solvelp(model, x)
    optimize!(model)
    return (
        status=termination_status(model),
        objval=objective_value(model),
        sol=value.(x)
    )
end

# #-------------------------------------------------------------------------------------------

"""
    buildCobraLP(model, solver)

Build a model by interfacing directly with the GLPK solver

# INPUTS

- `model`:          An `::LPproblem` object that has been built using the `loadModel` function.
                        All fields of `model` must be available.
- `solver`:         A `::SolverConfig` object that contains a valid `handle`to the solver

# OUTPUTS

- `model`:          An `::LPproblem` object that has been built using the JuMP.
- `x`:              primal solution vector
- `c`:              The objective vector, always in the sense of minimization

# EXAMPLES

```julia
julia> model, x, c = buildCobraLP(model, solver)
```

See also: `buildlp()`
"""

function buildCobraLP(model, solver::SolverConfig)

    if solver.handle != -1
        # prepare the csense vector when letters instead of symbols are used
        for i = 1:length(model.csense)
            if model.csense[i] == 'E'
                model.csense[i] = '='
            end
            if model.csense[i] == 'G'
                model.csense[i] = '>'
            end
            if model.csense[i] == 'L'
                model.csense[i] = '<'
            end
        end
        return buildlp(model.osense * model.c, model.S, model.csense, model.b, model.lb, model.ub, solver.handle)
    else
        error("The solver is not supported. Please set solver name to one the supported solvers.")
    end

end

#-------------------------------------------------------------------------------------------
"""
    changeCobraSolver(name, params, printLevel)

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

function changeCobraSolver(name, params=[]; printLevel::Int=1)
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

#-------------------------------------------------------------------------------------------
"""
    solveCobraLP(model, solver)

Function used to solve a linear program (LP) with a specified solver.
LP problem must have the form:
```
                                  max/min cᵀv
                                   s.t.  Av = b
                                        l ⩽ v ⩽ u
```
# INPUTS

- `model`:          An `::LPproblem` object that has been built using the `loadModel` function.
                        All fields of `model` must be available.
- `solver`:         A `::SolverConfig` object that contains a valid `handle`to the solver

# OUTPUTS

- `status`:         Termination status
- `objval`:         Optimal objective value
- `sol`:            Primal solution vector

# EXAMPLES

Minimum working example
```julia
julia> status, objval, sol = solveCobraLP(model, solver)
```

See also: `solvelp()`,
"""

function solveCobraLP(model, solver)

    if solver.handle != -1

        # retrieve the solution
        m, x, c = buildCobraLP(model, solver)
        status, objval, sol = solvelp(m, x)

        # adapt the objective value
        if status == :Optimal
            objval = model.osense * objval
        end
        return status, objval, sol
    else
        error("The solver handle is not set properly using `changeCobraSolver()`.")
    end

end

# export buildlp, solvelp, linprog, buildCobraLP, changeCobraSolver, solveCobraLP, autoTuneSolver

# #-------------------------------------------------------------------------------------------
