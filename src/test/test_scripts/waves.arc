Define basic as f(x) = sin(x)
@basic from -PI to PI
for i from 1 to 10 {
  @transform basic to basic + sin(i*x)
}
