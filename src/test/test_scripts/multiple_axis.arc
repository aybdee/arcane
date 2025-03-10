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
