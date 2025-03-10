
# Arcane Programming Language Syntax

Arcane is a specialized programming language for creating animations and visualizations in STEM fields. It currently supports defining mathematical functions, animating values, and visualizing them on axes. Below is an overview of the language syntax and features.

## Current Features(updated as features are added)
- Define regular and parametric mathematical functions.
- Animate values over specified intervals.
- Plot functions as part of animations.
- Support for multiple axes, laid out horizontally by default.
- Variables for storing numeric values or expressions.

## Syntax Guide

### 1. Defining Functions

#### Regular Functions
Define a regular function using the syntax:
```plaintext
Define <name> as f(x) = <expression>
```
**Example:**
```plaintext
Define quadratic as f(x) = x ^ 2
```

#### Parametric Functions
Define a parametric function using the syntax:
```plaintext
Define <name> as parametric (t) = (<x-expression>, <y-expression>)
```
**Example:**
```plaintext
Define lissajous as parametric (t) = (sin(3 * t), cos(2 * t))
```

### 2. Animating Values
Animate a value over a specific interval using the syntax:
```plaintext
@<value_name> from <start> to <end>
```
If the value is a mathematical function, it will be plotted over the specified interval.

**Example:**
```plaintext
@quadratic from -2 to 2
@lissajous from 0 to 2 * PI
```

### 3. Using Axes
Functions can be grouped and visualized on axes. Define axes using the syntax:
```plaintext
on axis <axis_name> {
  @<value_name> from <start> to <end>
  ...
}
```
**Example:**
```plaintext
on axis banana {
  @rose from 0 to 2 * PI
  @epicycloid from 0 to 2 * PI
}

on axis plantain {
  @lissajous from 0 to 2 * PI
  @heart from 0 to 2 * PI
}
```

### 4. Variable Definitions
Variables can store numeric literals or mathematical expressions:
```plaintext
Define <variable_name> as <value>
```
**Example:**
```plaintext
Define a as 5
Define b as 3 * PI
```

### 5. Supported Types
- **Number literals:** Any numeric value (e.g., `1`, `3.14`, `2 * PI`).
- **Mathematical functions:** Regular functions (`f(x)`) and parametric functions (`parametric(t)`).

### 6. Examples
#### Example Program 1:
```plaintext
Define lissajous as parametric (t) = (sin(3 * t), cos(2 * t))
Define epicycloid as parametric (t) = ((5 + 1) * cos(t) - cos(5 * t), (5 + 1) * sin(t) - sin(5 * t))
Define rose as parametric (t) = (cos(4 * t) * cos(t), cos(4 * t) * sin(t))
Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

on axis banana {
  @rose from 0 to 2 * PI
  @epicycloid from 0 to 2 * PI
}

on axis plantain {
  @lissajous from 0 to 2 * PI
  @heart from 0 to 2 * PI
}
```

#### Example Program 2:
```plaintext
Define cycloid as parametric (t) = (t - sin(t), 1 - cos(t))
@cycloid from 0 to 2 * PI

Define quadratic as f(x) = x ^ 2
@quadratic from -2 to 2

Define sine_wave as f(x) = sin(x)
@sine_wave from -2 * PI to 2 * PI

Define heart as parametric (t) = (16 * sin(t) ^ 3, 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))
@heart from 0 to 2 * PI
```

## Notes
- Default axes layout is horizontal. Custom layouts are planned for future updates.
- Use mathematical constants like `PI` and `e` directly in expressions.
- Ensure proper intervals when animating values to avoid errors.

