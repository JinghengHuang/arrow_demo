# OptimizationServer (Julia)

This project implements a lightweight optimization server using [JuMP.jl](https://jump.dev/) and [iHighs.jl](https://github.com/jump-dev/HiGHS.jl). The server listens for incoming socket connections and sends optimization results serialized in Arrow IPC format.

## 📁 Project Structure
```
project/
├── Project.toml # Project dependencies (JuMP, DataFrames, etc.)
├── Manifest.toml # Dependency lock file (auto-generated)
├── engine.jl # Entry point to start the server
├── optimization_server.jl # Main module: defines start_server
└── solve.jl # Contains optimization logic
```

- solve.jl contains the optimization model logic.
- optimization_server.jl defines the OptimizationServer module and exports start_server().
- engine.jl is the execution entry point that includes the server module and starts the service.



## 🚀 Getting Started

### 1.  Launch Julia in project mode
```julia --project=.```
This tells Julia to use the current folder's environment (Project.toml + Manifest.toml).

### 2. Install dependencies (only needed the first time)
```julia```

Once inside Julia REPL:

```julia> ]```
```(pkg) instantiate```

### 3. Start the server directly from terminal:

```julia --project=. engine.jl```

You should see:
```Listening on 127.0.0.1:65432```

