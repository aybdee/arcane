# Define base shapes
Define center as point at (0,0)
Define outer_boundary as circle with radius 3 at (0,0)
Define inner_shape as regular polygon with radius 2 and sides 6 at (0,0)

# Create construction
@center
@outer_boundary
@inner_shape

# Add measurements and labels
@write "Center" below center with size 16
@write "Hexagon" above inner_shape with size 18
# @line from center to (2,0)
@write "r = 2" at (1,0.2) with size 14
