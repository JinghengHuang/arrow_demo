# OptimizationServer (Julia)

This project implements a lightweight socket-based optimization server. It receives optimization problems (e.g. LP, QP) encoded in Arrow IPC format via TCP, solves them using JuMP and solver backends, and returns the result. The server listens for incoming socket connections and sends optimization results serialized in Arrow IPC format.

## 📁 Project Structure
```
julia/
├── controller/ # Request listener/controller
│ └── socket_server.jl # TCP socket server (entry controller)
│
├── model/ # Optimization model definitions
│ ├── lp_model.jl
│ └── qp_model.jl
│
├── service/ # Business logic and factories
│ ├── model_factory.jl # Maps model type strings to model modules
│ ├── solver_factory.jl # Maps solver name to JuMP optimizer
│ └── optimization_service.jl # Core compute logic
│
├── utils/ # Reusable I/O and math helpers
│ ├── io_utils.jl # Arrow serialization, TCP helpers
│ └── sparse_matrix.jl # Sparse array converters
│
├── engine.jl # Project entry point
├── Project.toml
└── Manifest.toml
```



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

