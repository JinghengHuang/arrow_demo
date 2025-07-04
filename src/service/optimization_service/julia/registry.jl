# registry.jl
module Registry

const MODEL_REGISTRY = Dict{String,Function}()

function register_model(name::String, builder::Function)
    MODEL_REGISTRY[name] = builder
end

function get_builder(name::String)
    return get(MODEL_REGISTRY, name, nothing)
end

end
