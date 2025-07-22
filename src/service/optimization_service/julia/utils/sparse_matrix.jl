# Construct sparse matrices
function to_sparse(mat)
    row = Vector{Int64}(mat[:row]) .+ 1
    col = Vector{Int64}(mat[:col]) .+ 1
    val = Vector{Float64}(mat[:val])
    nrow = maximum(row)
    ncol = maximum(col)
    sparse(row, col, val, nrow, ncol)
end