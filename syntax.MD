# Arcane Programming Language - Complete Syntax Guide
Arcane is a specialized domain-specific language (DSL) designed for creating mathematical animations, visualizations, and geometric constructions in STEM education. It provides an intuitive syntax for defining mathematical functions, creating geometric shapes, and animating mathematical concepts.

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Variable and Constant Definitions](#variable-and-constant-definitions)
3. [Function Definitions](#function-definitions)
4. [Animation and Plotting](#animation-and-plotting)
5. [Coordinate Systems](#coordinate-systems)
6. [Geometric Shapes](#geometric-shapes)
7. [Positional Relationships](#positional-relationships)
8. [Text and Annotations](#text-and-annotations)
9. [Visual Enhancements](#visual-enhancements)
10. [Function Transformations](#function-transformations)
11. [Mathematical Expressions](#mathematical-expressions)
12. [Best Practices](#best-practices)

## Core Concepts

Arcane operates on the principle of **define-then-use**: you define mathematical functions, geometric shapes, and constants, then animate or display them using the `@` operator.

### Basic Structure
```arcane
Define <name> as <definition>
@<name> [with options]
```

## Variable and Constant Definitions

### Mathematical Constants
```arcane
Define e as 2.71828
Define pi_half as PI / 2
Define custom_constant as 42
```

### Point Definitions
```arcane
Define origin as point at (0,0)
Define corner as point at (2,3)
```

## Function Definitions

### Regular Functions
Standard mathematical functions of one variable:
```arcane
Define <name> as f(x) = <expression>
```

**Examples:**
```arcane
Define quadratic as f(x) = x ^ 2
Define cubic as f(x) = x ^ 3
Define sine_wave as f(x) = sin(x)
Define exponential as f(x) = e ^ x
Define complex_function as f(x) = 2 * ((x - 5) ^ 2)
Define damped_oscillation as f(x) = e ^ (-0.1 * x) * sin(x)
Define bell_curve as f(x) = e ^ (-x ^ 2)
```

### Parametric Functions
Functions that define curves using a parameter t:
```arcane
Define <name> as parametric (t) = (<x-expression>, <y-expression>)
```

**Examples:**
```arcane
Define cycloid as parametric (t) = (t - sin(t), 1 - cos(t))
Define ellipse as parametric (t) = (3 * cos(t), 2 * sin(t))
Define lissajous as parametric (t) = (sin(3 * t), cos(2 * t))
Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
Define rose as parametric (t) = (cos(4 * t) * cos(t), cos(4 * t) * sin(t))
Define epicycloid as parametric (t) = ((5 + 1) * cos(t) - cos(5 * t), (5 + 1) * sin(t) - sin(5 * t))
Define log_spiral as parametric (t) = (e ^ t * cos(t), e ^ t * sin(t))
Define carotid as parametric (t) = (e * cos(t) * (1 - cos(t)), e * sin(t) * (1 - cos(t)))
```

### Polar Functions
Functions in polar coordinates:
```arcane
Define <name> as polar(t) = <r-expression>
```

**Examples:**
```arcane
Define polly as polar(t) = 2 * sin(5 * t)
Define spiral as polar(t) = t
```

## Animation and Plotting

### Basic Function Plotting
```arcane
@<function_name> from <start> to <end>
```

**Examples:**
```arcane
@quadratic from -2 to 2
@sine_wave from -2 * PI to 2 * PI
@cycloid from 0 to 2 * PI
@heart from 0 to 2 * PI
```

### Animated Dot Sweeping
Animate a dot moving along the function curve:
```arcane
@<function_name> from <start> to <end> and sweep dot across
```

**Examples:**
```arcane
@quadratic from 0 to 100 and sweep dot across
@simple_equation from -5 to 5 and sweep dot across
```

### Inline Function Definitions
Define and plot functions in a single line:
```arcane
@f(x) = <expression> from <start> to <end> [and sweep dot across]
```

**Examples:**
```arcane
@f(x) = x ^ 2 from -2 to 2 and sweep dot across
@f(x) = 2 * (x ^ 3) from -2 to 2 and sweep dot across
```

## Coordinate Systems

### Cartesian Axes
```arcane
on axis <axis_name> {
    @<function_name> from <start> to <end>
    # Multiple functions can be plotted on the same axis
    @<another_function> from <start> to <end>
}
```

**Examples:**
```arcane
on axis first_axis {
    @simple_equation from -2 * PI to 2 * PI
    @show 10 vertical lines on simple_equation from -1 * PI to PI
}

on axis banana {
    @rose from 0 to 2 * PI
}

on axis plantain {
    @lissajous from 0 to 2 * PI
    @heart from 0 to 2 * PI
}
```

### Polar Coordinate Systems
```arcane
on polar <polar_name> {
    @<polar_function> from <start> to <end>
}
```

**Examples:**
```arcane
on polar pollinus {
    @polly from 0 to 2 * PI
}
```

### Multi-Axis Layouts
Multiple coordinate systems can be used simultaneously:
```arcane
on axis axis_one {
    @f(x) = x ^ 2 from -2 to 2
}

on axis axis_two {
    @f(x) = sin(x) from -PI to PI
}

on polar polar_one {
    @polar(t) = 2 * sin(5 * t) from 0 to 2 * PI
}
```

## Geometric Shapes

### Basic Shapes

#### Points
```arcane
@point at (<x>, <y>)
```

#### Lines
```arcane
# Line between two points
@line from (<x1>, <y1>) to (<x2>, <y2>)
@line from <point1> to <point2>

# Line with angle and length
@line from (<x>, <y>) with angle <angle> and length <length>
```

#### Rectangles and Squares
```arcane
@square with length <length> at (<x>, <y>)
@rectangle with width <width> and height <height> at (<x>, <y>)
```

#### Circles
```arcane
@circle with radius <radius> at (<x>, <y>)
```

#### Polygons
```arcane
# Regular polygons
@regular polygon with radius <radius> and sides <sides> at (<x>, <y>)

# Irregular polygons
@polygon with points (<x1>, <y1>), (<x2>, <y2>), ..., (<xn>, <yn>)
```

#### Angles
```arcane
# Angle at a point between two other points
@angle at (<x>, <y>) from (<x1>, <y1>) to (<x2>, <y2>)

# Angle with specified direction and length
@angle from (<x>, <y>) with angle <angle> and length <length>
```

#### Arrows
```arcane
@arrow from (<x1>, <y1>) to (<x2>, <y2>)
@arrow from <point1> to <point2>
```

### Shape Storage and Reuse
Shapes can be defined and reused:
```arcane
Define <shape_name> as <shape_definition>
@<shape_name>
```

**Examples:**
```arcane
Define my_point as point at (3,3)
Define my_square as square with length 1 at (3,3)
Define my_rectangle as rectangle with width 2 and height 1 at (3,3)
Define my_hexagon as regular polygon with radius 1 and sides 7 at (3,3)
Define my_polygon as polygon with points (3,3), (4,3), (4,4), (3,4)

@my_point
@my_square
@my_rectangle
```

## Positional Relationships

Shapes can be positioned relative to other objects:

```arcane
Define base_point as point at (0,0)
Define above_square as square with length 1 above base_point
Define left_rectangle as rectangle with width 2 and height 1 left of base_point
Define right_hexagon as regular polygon with radius 1 and sides 6 right of base_point
Define below_circle as circle with radius 1 below base_point
```

**Positional Keywords:**
- `above`
- `below` 
- `left of`
- `right of`
- `on` (for positioning on curves or other shapes)

**Special Positioning:**
```arcane
# Position shapes on circles at specific angles
@square with length 1 on outer_circle at angle PI / 2

# Position shapes on function curves
@square with length 1 above sine_wave
```

## Text and Annotations

### Basic Text
```arcane
@write "<text>" at (<x>, <y>) with size <size>
@write "<text>" above <object> with size <size>
@write "<text>" below <object> with size <size>
```

**Examples:**
```arcane
@write "This is a sine wave" at (0,0) with size 20
@write "This is a sine wave" above sine_wave with size 30
@write "m1" above mini_circle with size 20
```

### LaTeX Expressions
```arcane
@write latex "<latex_expression>" above <object>
@write latex "<latex_expression>" at (<x>, <y>) with size <size>
```

**Examples:**
```arcane
@write latex "\frac{2}{2}" above square with size 20
@write latex "\frac{2}{2} + \frac{1}{2} * sin(20)" above axalia
```

## Visual Enhancements

### Vertical Lines on Functions
Add visual guides to function plots:
```arcane
@show <number> vertical lines on <function_name> from <start> to <end>
```

**Examples:**
```arcane
@show 10 vertical lines on simple_equation from -1 * PI to PI
@show 20 vertical lines on other_equation from -1 * PI to PI
```

### Shape Styling
Shapes can have custom styling:
```arcane
Define styled_shape as <shape_definition> and style {
    fill: "<color>"
    stroke_color: "<color>"
}
```

**Example:**
```arcane
Define inner_circle as circle with radius 0.5 at (0,0) and style {
    fill: "red"
    stroke_color: "red"
}
```

## Function Transformations

Functions can be transformed by adding or modifying their expressions:
```arcane
@transform <function_name> to <new_expression>
```

**Example:**
```arcane
Define basic as f(x) = sin(x)
@basic from -PI to PI
@transform basic to basic + sin(x)
@transform basic to basic + sin(2*x)
@transform basic to basic + sin(3*x)
```

## Mathematical Expressions

### Operators
- **Addition:** `+`
- **Subtraction:** `-`
- **Multiplication:** `*`
- **Division:** `/`
- **Exponentiation:** `^`
- **Parentheses for grouping:** `(`, `)`

### Built-in Functions
- **Trigonometric:** `sin(x)`, `cos(x)`, `tan(x)`
- **Exponential:** `e ^ x`
- **Logarithmic:** `log(x)`

### Constants
- **Pi:** `PI` (3.14159...)
- **Euler's number:** `e` (2.71828...)
- **Custom constants can be defined**

### Complex Expressions
```arcane
# Nested functions and operations
Define complex as f(x) = e ^ (-0.1 * x) * sin(x)
Define polynomial as f(x) = 2 * ((x - 5) ^ 2)
Define combined as f(x) = sin(x) + cos(2*x) + 0.5*sin(4*x)

# Parametric expressions with multiple operations
Define complex_parametric as parametric (t) = (
    16 * sin(t) ^ 3, 
    13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)
)
```

## Best Practices

### Naming Conventions
- Use descriptive names for functions and shapes
- Use snake_case for multi-word names
- Keep axis names concise but meaningful

### Organization
- Group related functions on the same axis
- Define constants at the beginning of scripts
- Use consistent spacing and indentation within axis blocks

### Mathematical Considerations
- Choose appropriate domains for functions
- Consider function behavior at boundaries
- Use parentheses to ensure correct operator precedence
- Test parametric functions over full parameter ranges

### Visual Design
- Use appropriate text sizes for readability
- Consider color coding for related elements
- Use consistent styling across similar shapes
- Space multiple axes appropriately

### Performance
- Avoid overly complex expressions in tight animation loops
- Use reasonable parameter ranges for smooth animations
- Consider the computational cost of nested function calls

## Example Scripts

### Complete Mathematical Visualization
```arcane
Define e as 2.71828

# Define multiple related functions
Define cycloid as parametric (t) = (t - sin(t), 1 - cos(t))
Define sine_wave as f(x) = sin(x)
Define exponential as f(x) = e ^ x

# Create multi-axis layout
on axis main_functions {
    @sine_wave from -2 * PI to 2 * PI and sweep dot across
    @show 8 vertical lines on sine_wave from -PI to PI
}

on axis parametric_curves {
    @cycloid from 0 to 4 * PI
}

on axis exponential_growth {
    @exponential from -2 to 2
}

# Add annotations
@write "Sine Wave with Animation" above main_functions with size 24
@write latex "e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!}" above exponential_growth
```

### Geometric Construction
```arcane
# Define base shapes
Define center as point at (0,0)
Define outer_boundary as circle with radius 3 at (0,0)
Define inner_shape as regular polygon with radius 2 and sides 6 at (0,0)

# Create construction
@center
@outer_boundary
@inner_shape

# Add measurements and labels
@write "Center" below center with size 16
@write "Hexagon" above inner_shape with size 18
@line from center to (2,0)
@write "r = 2" at (1,0.2) with size 14
```

This comprehensive syntax guide covers all the features demonstrated in your test scripts and provides a solid foundation for users to create complex mathematical visualizations and animations with Arcane.
