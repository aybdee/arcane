Define small_circle as circle with radius 4 at (0,0)
Define hexagon as regular polygon with radius 1 and sides 7 at (3,3) 

@show small_circle
@show hexagon
@rotate hexagon by PI / 4

@move hexagon above small_circle

@transform small_circle to square with length 1 at (0, 0)
@scale hexagon by 2
