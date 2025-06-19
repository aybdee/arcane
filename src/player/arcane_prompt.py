ARCANE_PROMPT = """
You are an LLM writing code in the Arcane programming language.
Arcane is a domain-specific language for creating mathematical, geometric, and physics-based visualizations. It supports reusable definitions, structured contexts, animations, and visual effects.
You should only output Arcane code, and nothing else — no explanations, no comments.
Your output will be used to generate videos, so:

- Ensure animations are visually clear and dynamic.
- Avoid overlapping elements unless intentional.
- Position and sequence visuals to explain the concept effectively.
- Make good use of motion, transformation, and labeling for clarit

Here are examples to illustrate the style and structure of Arcane code:
=== ./test_scripts/carotid_and_rose.arc ===
Define carotid as parametric (t) = (e * cos(t) * (1 - cos(t)), e * sin(t) * (1 - cos(t)))
@carotid from 0 to 2 * PI and sweep dot across


=== ./test_scripts/define.arc ===
Define cubic as f(x) = x ^ 3
@cubic from -1 to 1


=== ./test_scripts/parametric_functions.arc ===
Define e as 2.71828
Define carotid as parametric (t) = (e * cos(t) * (1 - cos(t)), (e * sin(t)) * (1 - cos(t)))
@carotid from 0 to 2 * PI


=== ./test_scripts/simple_math.arc ===
Define quadratic as f(x) = 2 * ((x - 5) ^ 2) 
@quadratic from 0 to 100 and sweep dot across




=== ./test_scripts/rose.arc ===
Define rose as parametric (t) = (cos(4 * t) * cos(t), cos(4 * t) * sin(t))
@rose from 0 to 2 * PI


=== ./test_scripts/function_test.arc ===
Define cycloid as parametric (t) = (t - sin(t), 1 - cos(t))
@cycloid from 0 to 2 * PI

Define lissajous as parametric (t) = (sin(3 * t), cos(2 * t))
@lissajous from 0 to 2 * PI

Define epicycloid as parametric (t) = ((5 + 1) * cos(t) - cos(5 * t), (5 + 1) * sin(t) - sin(5 * t))
@epicycloid from 0 to 2 * PI

Define rose as parametric (t) = (cos(4 * t) * cos(t), cos(4 * t) * sin(t))
@rose from 0 to 2 * PI

Define ellipse as parametric (t) = (3 * cos(t), 2 * sin(t))
@ellipse from 0 to 2 * PI

Define quadratic as f(x) = x ^ 2
@quadratic from -2 to 2

Define cubic as f(x) = x ^ 3
@cubic from -2 to 2

Define sine_wave as f(x) = sin(x)
@sine_wave from -2 * PI to 2 * PI

Define cosine_wave as f(x) = cos(x)
@cosine_wave from -2 * PI to 2 * PI

Define exponential as f(x) = e ^ x
@exponential from -1 to 1

Define damped_oscillation as f(x) = e ^ (-0.1 * x) * sin(x)
@damped_oscillation from 0 to 20

Define piecewise_parabola as f(x) = (x ^ 2) + 3 * x + 2
@piecewise_parabola from -3 to 3

Define bell_curve as f(x) = e ^ (-x ^ 2)
@bell_curve from -2 to 2

Define log_spiral as parametric (t) = (e ^ t * cos(t), e ^ t * sin(t))
@log_spiral from 0 to 2 * PI

Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
@heart from 0 to 2 * PI


=== ./test_scripts/parametric_function_test.arc ===
Define epicycloid as parametric (t) = ((5 + 1) * cos(t) - cos(5 * t), (5 + 1) * sin(t) - sin(5 * t))
@epicycloid from 0 to 2 * PI

Define ellipse as parametric (t) = (3 * cos(t), 2 * sin(t))
@ellipse from 0 to 2 * PI

Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
@heart from 0 to 2 * PI


=== ./test_scripts/cycloids.arc ===
Define cycloid as parametric (t) = (t - sin(t), 1 - cos(t))
@cycloid from -4 * PI to 4 * PI


=== ./test_scripts/scratch_pad.arc ===
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


=== ./test_scripts/dot_sweep.arc ===
Define simple_equation as f(x) = sin(x)
on axis one { 
    @simple_equation from -5 to 5 and sweep dot across
}


=== ./test_scripts/math_scratch_pad.arc ===
Define polly as polar(t) = 2 * sin(5 * t)
Define simple_equation as f(x)  = 2 * (x ^ 3) 

on polar first_polar_axis { 
  @polly from 0 to 2 * PI
}

on axis another_axis { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}

on axis one_more { 
  @simple_equation from -2 to 2 and sweep dot across
  @show 10 vertical lines on simple_equation from -1 to 1
}




=== ./test_scripts/multiple_axis.arc ===
Define lissajous as parametric (t) = (sin(3 * t), cos(2 * t))
Define epicycloid as parametric (t) = ((5 + 1) * cos(t) - cos(5 * t), (5 + 1) * sin(t) - sin(5 * t))
Define rose as parametric (t) = (cos(4 * t) * cos(t), cos(4 * t) * sin(t))
Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))


on axis banana {
  @rose from 0 to 2 * PI
}

on axis plantain {
  @lissajous from 0 to 2 * PI
  @heart from 0 to 2 * PI
}


=== ./test_scripts/vertical_lines.arc ===
Define simple_equation as f(x) = sin(x)
Define other_equation as f(x) = cos(x)

on axis first_axis {
  @simple_equation from -2 * PI to 2 * PI
  @show 10 vertical lines on simple_equation from -1 * PI to PI
}


on axis second_axis {
  @other_equation from -2 * PI to 2 * PI
  @show 20 vertical lines on other_equation from -1 * PI to PI
}


=== ./test_scripts/polar.arc ===
Define polly as polar(t) = 2 * sin(5 * t)
on polar pollinus { 
  @polly from 0 to 2 * PI
}

on axis axis_one { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}


on axis axis_two { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}

@square with length 1 at (0,0)




=== ./test_scripts/text.arc ===
Define sine_wave as f(x) = sin(x)

on axis axalia {
  @sine_wave from -2 * PI to 2 * PI
}

@square with length 1 above sine_wave 

@write "This is a sine wave" at (0,0) with size 20
@write "This is a sine wave" above sine_wave with size 30



=== ./test_scripts/latex.arc ===
Define sine_wave as f(x) = sin(x)

on axis axalia {
  @sine_wave from -2 * PI to 2 * PI
}

@write latex "\frac{2}{2} + \frac{1}{2} * sin(20)" above axalia


=== ./test_scripts/fibonacci_lines.arc ===
@line from (0.00, 0.00) with angle 0 and length 0.1
@line from (0.10, 0.00) with angle 1.5708 and length 0.1
@line from (0.10, 0.10) with angle 3.14159 and length 0.2
@line from (-0.10, 0.10) with angle -1.5708 and length 0.3
@line from (-0.10, -0.20) with angle 0 and length 0.5
@line from (0.40, -0.20) with angle 1.5708 and length 0.8
@line from (0.40, 0.60) with angle 3.14159 and length 1.3
@line from (-0.90, 0.60) with angle -1.5708 and length 2.1
@line from (-0.90, -1.50) with angle 0 and length 3.4
@line from (2.50, -1.50) with angle 1.5708 and length 5.5
@line from (2.50, 4.00) with angle 3.14159 and length 8.9
@line from (-6.40, 4.00) with angle -1.5708 and length 14.4


=== ./test_scripts/lines.arc ===
Define one as point at (0,0)
Define two as point at (2,0)
@line from one to two


=== ./test_scripts/elbow.arc ===
@angle from (0, 0) with angle PI / 4 and length 2



=== ./test_scripts/shapes.arc ===
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
Define my_hexagon as regular polygon with radius 1 and sides 7 at (3,3) 
Define my_polygon as polygon with points (3,3), (4,3), (4,4), (3,4)

# Use stored shapes
@my_point
@my_square
@my_rectangle
@my_hexagon
@my_polygon


=== ./test_scripts/waves.arc ===
Define basic as f(x) = sin(x)
@basic from -PI to PI
@transform basic to basic + sin(x)
@transform basic to basic + sin(2*x)
@transform basic to basic + sin(3*x)
@transform basic to basic + sin(4*x)
@transform basic to basic + sin(5*x)
@transform basic to basic + sin(6*x)
@transform basic to basic + sin(7*x)
@transform basic to basic + sin(8*x)
@transform basic to basic + sin(9*x)




=== ./test_scripts/ed/newtons_law.arc ===
Define outer_circle as circle with radius 2 at (0,0)
Define inner_circle as circle with radius 0.5 at (0,0) and style {
  fill: "red"
  stroke_color: "red"
}

Define mini_circle as circle with radius 0.1 on outer_circle at angle 2*PI and style {
  fill: "red"
  stroke_color: "red"
}

@write "m1" above mini_circle with size 20
@write "m2" above inner_circle with size 20
clear mini_circle


=== ./test_scripts/test.arc ===
@point at (0,0)
@point at (2,0)

@line from (0,0) to (2,0)
@line from (0,0) with angle PI/4 and length 2

@angle at (0,0) from (1,0) to (1,1)
@angle from (0,0) with angle PI/3 and length 1

@square with length 1 at (0,0) 
@rectangle with width 2 and height 1 at (1,1)

@regular polygon with radius 1 and sides 3 at (0,0) 
@regular polygon with radius 1 and sides 6 at (2,0)

@polygon with points (0,0), (1,0), (1,1), (0,1)


=== ./test_scripts/relative_shapes.arc ===
Define my_point as point at (0,0)
Define my_square as square with length 1 below my_point
Define my_rectangle as rectangle with width 2 and height 1 left of my_point
Define my_hexagon as regular polygon with radius 1 and sides 6 right of my_point

@my_hexagon


=== ./test_scripts/arrow.arc ===
Define point1 as point at (0,0)
Define point2 as point at (2,2)
@arrow from point1 to point2 
clear point1


=== ./test_scripts/transform.arc ===
Define square_1 as square with length 1 at (0, 0)
Define circle_1 as circle with radius 1 at (1, 1)
@transform square_1 to circle_1
@transform circle_1 to square_1


=== ./test_scripts/optics.arc ===
Define convex_lens as lens with focal length -1 and thickness 1 at (-1,0) 
Define concave_lens as lens with focal length 1 and thickness 1 right of convex_lens
Define second_convex as lens with focal length -1 and thickness 1 right of concave_lens

@convex_lens
@concave_lens
@second_convex

Define incoming_rays as rays from (-4, -0.2) to (-4, 0.2) with direction RIGHT and count 4
@propagate incoming_rays through convex_lens then concave_lens

@write "rays diverge" below convex_lens with size 20
@write "rays converge" above concave_lens with size 20
@write "rays diverge again" below second_convex  with size 20


=== ./test_scripts/op.arc ===
Define convex_lens as lens with focal length -1 and thickness 1 at (-1,0) 
Define concave_lens as lens with focal length 1 and thickness 1 right of convex_lens
Define second_convex as lens with focal length -1 and thickness 1 right of concave_lens

@convex_lens
@concave_lens
@second_convex

Define incoming_rays as rays from (-4, -0.2) to (-4, 0.2) with direction RIGHT and count 4
@propagate incoming_rays through convex_lens then concave_lens

@write "rays diverge" below convex_lens with size 20
@write "rays converge" above concave_lens with size 20
@write "rays diverge again" below second_convex  with size 20


=== ./test_scripts/area.arc ===
Define simple_equation as f(x) = 2 * sin(x)
@simple_equation from -4 * PI to 2 * PI
@show 20 vertical lines on simple_equation from -1 * PI to PI


=== ./test_scripts/motion.arc ===
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




=== ./test_scripts/scale_rotate.arc ===
Define square as square with length 1 at (0, 0)
@scale square by 0.5
@rotate square by PI / 4
@transform square to circle with radius 4 at (0,0)


=== ./test_scripts/brace.arc ===
Define line as line from (0,0) to (3,3)
@brace on line with text "straight line"


=== ./test_scripts/electric.arc ===
Define electric_potential as charge with magnitude 1 at (2,-1)
@electric_potential
@charge with magnitude 1 at (0,1)
@charge with magnitude -4 at (1,2)
@move electric_potential to (3,3)
@move electric_potential to (-1,1)
"""
