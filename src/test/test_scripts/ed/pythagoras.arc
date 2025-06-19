# Define triangle points
Define A as point at (0, 0)
Define B as point at (4, 0)
Define C as point at (0, 3)

# Define triangle sides
Define AB as line from A to B
Define BC as line from B to C
Define CA as line from C to A

@AB
@BC
@CA

# Define squares along each side
Define square_AB as square with length 4 below AB
Define square_CA as square with length 3 left of CA
Define square_BC as square with length 5 above BC

# Side labels
@write "a" below AB with size 20
@write "b" left of CA with size 20
@write "c" above BC with size 20

# Rotate squares to align with triangle sides
@rotate square_AB by 0
@rotate square_CA by PI / 2
@rotate square_BC by -1 * atan(3 / 4)

# Animate proof
@transform square_AB to square_BC
@transform square_CA to square_BC

# Conclusion
@write "a² + b² = c²" below square_BC with size 24
