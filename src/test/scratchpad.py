from manim import *


class SideBySideGraphs(Scene):
    def construct(self):
        # Axes and graphs for the first plot
        axes1 = Axes(x_range=[-3, 3], y_range=[-2, 2], tips=False)

        graph1 = axes1.plot(lambda x: x**2, color=BLUE, x_range=[-3, 3])

        # Axes and graphs for the second plot
        axes2 = Axes(x_range=[-3, 3], y_range=[-2, 2], tips=False).next_to(axes1)

        graph2 = axes2.plot(lambda x: 0.5 * x**3, color=RED, x_range=[-3, 3])

        # vgroup = VGroup(axes1, axes2, graph1, graph2).scale(0.5).move_to(ORIGIN)

        self.play(Create(axes1))
        self.play(Create(graph1))
        self.play(Create(axes2))
        self.play(Create(graph2))
