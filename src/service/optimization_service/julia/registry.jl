"""
# Registry.jl
# This module provides a registry for optimization model builders.
# It allows dynamic registration and retrieval of model builders based on their type.
# This is useful for extending the server with new model types without modifying the core code.
"""
module Registry

const MODEL_REGISTRY = Dict{String,Function}()

function register_model(name::String, builder::Function)
    MODEL_REGISTRY[name] = builder
end



function get_builder(name::String)
    return get(MODEL_REGISTRY, name, nothing)
end

end
