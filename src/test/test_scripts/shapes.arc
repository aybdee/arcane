@point at (0,0)
@point at (2,0)

@line from (0,0) to (2,0)
@line from (0,0) with angle PI/4 and length 2

@angle at (0,0) from (1,0) to (1,1)
@angle from (0,0) with angle PI/3 and length 1

@square at (0,0) with length 1
@rectangle with width 2 and height 1 below square

@regular polygon with radius 1 and sides 3 at (0,0) 
@regular polygon with radius 1 and sides 6 at (2,0)

@polygon with points (0,0), (1,0), (1,1), (0,1)

Define my_point as point at (3,3)
Define my_square as square at (3,3) with length 1
Define my_rectangle as rectangle with width 2 and height 1 at (3,3)
Define my_hexagon as regular polygon with radius 1 and sides 6 at (3,3)
Define my_polygon as polygon with points (3,3), (4,3), (4,4), (3,4)

@my_point
@my_square
@my_rectangle
@my_hexagon
@my_polygon
