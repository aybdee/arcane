Define sine_wave as f(x) = sin(x)

on axis axalia {
  @sine_wave from -2 * PI to 2 * PI
}

@square with length 1 above sine_wave 

@write "This is a sine wave" at (0,0) with size 20
@write "This is a sine wave" above sine_wave with size 30

