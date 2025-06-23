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


