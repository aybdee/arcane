Define circle_1 as circle with radius 1 at (0, 0)
Define square_2 as square with length 1 at (0, 0)
Define rectangle as rectangle with width 2 and height 1 at (0, 0)
Define carotid as parametric (t) = (e * cos(t) * (1 - cos(t)), e * sin(t) * (1 - cos(t)))
Define smaller_square as square with length 0.2 at (0, 0)

@square_2
@move square_2 above circle_1
@rectangle

clear square_2
clear rectangle

@carotid from 0 to 2 * PI
@move smaller_square along carotid


