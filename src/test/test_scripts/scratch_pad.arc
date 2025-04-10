Define simple_equation as f(x) = sin(x)
@show vertical lines on simple_equation from -1 to 1

on axis one { 
    @simple_equation from -5 to 5 and sweep dot across
    @another_simple from -5 to 5 and sweep dot across
}
