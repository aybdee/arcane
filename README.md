# Arcane

Arcane is a domain-specific language designed for creating mathematical animations and visualizations. It provides an intuitive syntax for expressing mathematical concepts and creating engaging visual demonstrations.

## Features Overview

### Basic Functions

#### Regular Functions

```arcane
Define f as f(x) = x^2
Define g as f(x) = sin(x)

on axis quadratic {
    @f from -2 to 2
    @write "Quadratic Function" above quadratic
}
```

#### Parametric Functions

```arcane
Define circle as parametric(t) = (cos(t), sin(t))
Define spiral as parametric(t) = (t * cos(t), t * sin(t))

on axis parametric_plot {
    @circle from 0 to 2 * PI
    @spiral from 0 to 4 * PI
}
```

#### Polar Functions

```arcane
Define rose as polar(t) = 2 * sin(5 * t)
Define cardioid as polar(t) = 1 + cos(t)

on polar polar_plot {
    @rose from 0 to 2 * PI
    @cardioid from 0 to 2 * PI
}
```

### Mathematical Objects

#### Points and Lines

```arcane
Define p1 as point at (0,0)
Define p2 as point at (2,2)

@line from p1 to p2
@line from (0,0) with angle PI/4 and length 2
```

#### Angles

```arcane
@angle at (0,0) from (1,0) to (1,1)
@angle from (0,0) with angle PI/3 and length 1
```

#### Shapes

```arcane
// Square
@square at (0,0) with length 1

// Rectangle
@rectangle with width 2 and height 1 at (1,1)

// Regular polygon
@regular polygon with radius 1 and sides 6 at (2,0)

// Custom polygon
@polygon with points (0,0), (1,0), (1,1), (0,1)
```

### Animation Features

#### Function Plotting with Sweeping

```arcane
Define sine as f(x) = sin(x)

on axis animation {
    @sine from -2 * PI to 2 * PI and sweep dot across
    @show vertical lines on sine from -PI to PI
}
```

#### Function Transformations

```arcane
Define wave as f(x) = sin(x)

on axis transform {
    @wave from -PI to PI
    @transform wave to wave + cos(x)
    @transform wave to 2 * wave
}
```

### Text and Labels

#### Basic Text

```arcane
on axis plot {
    @f(x) = x^2 from -2 to 2
    @write "Quadratic Function" above plot
}
```

#### LaTeX Support

```arcane
@write latex "\frac{d}{dx}(x^2) = 2x" above plot
@write latex "\int_0^1 x^2 dx = \frac{1}{3}" below plot
```

### Example Mathematical Curves

#### Lissajous Curve

```arcane
Define lissajous as parametric(t) = (sin(3*t), sin(2*t))

on axis liss {
    @lissajous from 0 to 2 * PI
    @write "Lissajous Curve" above liss
}
```

#### Heart Curve

```arcane
Define heart as parametric(t) = (16 * sin(t)^3, 13 * cos(t) - 5 * cos(2*t) - 2 * cos(3*t) - cos(4*t))

on axis heart_plot {
    @heart from 0 to 2 * PI
    @write "Heart Curve" above heart_plot
}
```

#### Logarithmic Spiral

```arcane
Define spiral as polar(t) = e^(0.2 * t)

on polar spiral_plot {
    @spiral from 0 to 4 * PI
    @write "Logarithmic Spiral" above spiral_plot
}
```

### Complex Examples

#### Combined Visualization

```arcane
Define f as f(x) = sin(x)
Define g as f(x) = cos(x)

on axis trig {
    @f from -2 * PI to 2 * PI
    @g from -2 * PI to 2 * PI
    @show vertical lines on f from -PI to PI
    @write latex "y = sin(x)" at (-PI, 1)
    @write latex "y = cos(x)" at (-PI, -1)
}
```

#### Interactive Animation

```arcane
Define oscillator as f(x) = sin(x) * e^(-0.1 * x)

on axis damped {
    @oscillator from 0 to 4 * PI and sweep dot across
    @write "Damped Oscillation" above damped
    @show vertical lines on oscillator from 0 to 4 * PI
}
```

## Mathematical Constants

The following mathematical constants are built into Arcane:

- `PI`: π (3.14159...)
- `e`: Euler's number (2.71828...)

## Best Practices

1. Use meaningful names for functions and axes
2. Group related animations in the same axis block
3. Add descriptive labels to help explain the visualization
4. Use appropriate ranges for function plotting
5. Combine different features to create engaging demonstrations

## Getting Started

1. Install Arcane
2. Create a new .arc file
3. Write your first animation using the examples above
4. Run the file using the Arcane interpreter
