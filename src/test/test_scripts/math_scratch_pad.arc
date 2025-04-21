Define polly as polar(t) = 2 * sin(5 * t)
on polar one { 
  @polly from 0 to 2 * PI
}

on axis two { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}


on axis three { 
  @f(x) = x ^ 2 from -2 to 2 and sweep dot across
}

on axis four { 
  @f(x) = 2 * (x ^ 3) from -2 to 2 and sweep dot across
}


