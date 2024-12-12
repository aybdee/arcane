from manim import *


def clip_plot(csystem, plotfun, x_range=[-5,5,.01], **kwargs):
    grp = VGroup()
    dx = x_range[2]
    for xstart in np.arange(*x_range):
        snip = csystem.plot(
            plotfun,
            x_range = [xstart,xstart+dx,0.5*dx],
            **kwargs
        )
        if (snip.get_top()[1]>csystem.get_top()[1]) or (snip.get_bottom()[1]<csystem.get_bottom()[1]):
            snip.set_opacity(0)
        grp += snip
    return grp


CoordinateSystem.clip_plot = clip_plot
