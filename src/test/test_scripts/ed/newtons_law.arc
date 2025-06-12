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
