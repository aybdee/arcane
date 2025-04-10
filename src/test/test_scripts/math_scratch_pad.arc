Define polly as polar(t) = 2 * sin(5 * t)
on polar pollinus { 
  @polly from 0 to 2 * PI
}

on axis pollinus { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}

