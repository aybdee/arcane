# from manim import *
#
# class ParametricCurveExample(Scene):
#     def construct(self):
#         ax = Axes()
#         cardioid = ax.plot_parametric_curve(
#             lambda t: np.array(
#                 [
#                     np.exp(1) * np.cos(t) * (1 - np.cos(t)),
#                     np.exp(1) * np.sin(t) * (1 - np.cos(t)),
#                     0,
#                 ]
#             ),
#             t_range=[0, 2 * PI],
#             color="#0FF1CE",
#         )
#         self.add(ax, cardioid)
import numpy as np
from pprint import pprint
e = 2.71828
def parametric_values(t):
    x = e * np.cos(t) * (1 - np.cos(t))
    y = e * np.sin(t) * (1 - np.cos(t))
    z = 0  # z is always 0 in this case
    return x, y, z

# Evaluate the values for t from 1 to 10
t_values = np.linspace(1, 10, 10)  # 10 points from t=1 to t=10
values = [parametric_values(t) for t in t_values]
pprint(values)
