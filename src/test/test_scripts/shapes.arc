# Points
@point at (0,0)
@point at (2,0)

# Lines with different definitions
@line from (0,0) to (2,0)
@line from (0,0) with angle PI/4 and length 2

# Angles with different definitions
@angle at (0,0) from (1,0) to (1,1)
@angle from (0,0) with angle PI/3 and length 1

# Basic shapes
@square with length 1 at (0,0) 
@rectangle with width 2 and height 1 at (1,1)

# Regular polygons
@regular polygon with radius 1 and sides 3 at (0,0)  # Triangle
@regular polygon with radius 1 and sides 6 at (2,0)  # Hexagon

# Irregular polygon
@polygon with points (0,0), (1,0), (1,1), (0,1)

# Store and reuse shapes
Define my_point as point at (3,3)
Define my_square as square with length 1 at (3,3) 
Define my_rectangle as rectangle with width 2 and height 1 at (3,3)
Define my_hexagon as regular polygon with radius 1 and sides 6 at (3,3) and style {
  fill: "green"
}
Define my_polygon as polygon with points (3,3), (4,3), (4,4), (3,4)

# Use stored shapes
@my_point
@my_square
@my_rectangle
@my_hexagon
@my_polygon
