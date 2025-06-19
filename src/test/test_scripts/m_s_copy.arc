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


on axis even_one_more { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}





