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
