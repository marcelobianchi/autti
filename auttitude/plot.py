#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

from matplotlib.patches import Circle
from matplotlib.collections import LineCollection
from matplotlib.mlab import griddata

from .geometry import project_equal_area  # , read_equal_area


def clip_lines(data, clip_radius=1.1):
    """segment point pairs between inside and outside of primitive, for
    avoiding spurious lines when plotting circles."""
    radii = np.linalg.norm(data, axis=1)
    radii[np.isinf(radii)] = 100.
    radii[np.isnan(radii)] = 100.
    inside = radii < clip_radius
    results = []
    current = []
    for i, is_inside in enumerate(inside):
        if is_inside:
            current.append(data[i])
        elif current:
            results.append(current)
            current = []
    if current:
        results.append(current)
    return results


class ProjectionPlot(object):
    point_defaults = {'marker': 'o',
                      'c': '#000000',
                      'ms': 3.0}

    circle_defaults = {"linewidths": 0.8,
                       "colors": "#4D4D4D",
                       "linestyles": "-"}

    contour_defaults = {"cmap": "Reds",
                        "linestyles": "-",
                        "antialiased": True}

    def __init__(self, axis=None, projection=project_equal_area):
        self.projection = projection
        if axis is None:
            from matplotlib import pyplot as plt
            self.axis = plt.gca()
            self.clear_diagram()
        else:
            self.axis = axis

    def clear_diagram(self):
        """Clears the plot area and plot the primitive."""
        self.axis.cla()
        self.axis.axis('equal')
        self.axis.set_xlim(-1.1, 1.1)
        self.axis.set_ylim(-1.1, 1.1)
        self.axis.set_axis_off()
        self.plot_primitive()

    def plot_primitive(self):
        """Plots the primitive, center, NESW indicators and North."""
        self.primitive = Circle((0, 0), radius=1, edgecolor='black',
                                fill=False, clip_box='None',
                                label='_nolegend_')
        self.axis.add_patch(self.primitive)
        # maybe add a dict for font options and such...
        self.axis.text(0.01, 1.025, 'N', family='sans-serif', size='x-small',
                       horizontalalignment='center')
        x_cross = [0, 1, 0, -1, 0]
        y_cross = [0, 0, 1, 0, -1]
        self.axis.plot(x_cross, y_cross, 'k+', markersize=8,
                       label='_nolegend_')

    def plot_poles(self, vectors, **kwargs):
        """Plot points on the diagram. Accepts and passes aditional key word
        arguments to axis.plot."""
        x, y, z = np.transpose(vectors)
        X, Y = self.projection(vectors)
        # use the default values if not user input
        # https://stackoverflow.com/a/6354485/1457481
        options = dict(self.point_defaults.items() + kwargs.items())
        self.axis.plot(X, Y, linestyle='', **options)

    def plot_circles(self, circles, **kwargs):
        """plot a list of circles, either great or small"""
        # use the default values if not user input
        # https://stackoverflow.com/a/6354485/1457481
        options = dict(self.circle_defaults.items() + kwargs.items())
        projected_circles = [segment for circle in circles for segment in
                             clip_lines(np.transpose(self.projection(circle,
                                                     invert_positive=False)))]
        circle_collection = LineCollection(projected_circles,
                                           **options)
        circle_collection.set_clip_path(self.primitive)
        self.axis.add_collection(circle_collection)

    def plot_contours(self, nodes, count, n_data, n_contours=10, minmax=True,
                      percentage=True, contour_mode='fillover', resolution=250,
                      **kwargs):
        """Plot contours of a spherical count. Parameters are the counting
        nodes, the actual counts and the number of data points. Returns the
        matplotlib contour object for creating colorbar."""
        if percentage:
            count = 100.*count/n_data
        if minmax:
            intervals = np.linspace(count.min(), count.max(), n_contours)
        else:
            intervals = np.linspace(0, count.max(), n_contours)
        xi = yi = np.linspace(-1.1, 1.1, resolution)
        # maybe preselect nodes here on z tolerance
        X, Y = self.projection(nodes, invert_positive=False)
        zi = griddata(X, Y, count, xi, yi, interp='linear')
        # use the default values if not user input
        # https://stackoverflow.com/a/6354485/1457481
        options = dict(self.contour_defaults.items() + kwargs.items())

        contour_fill, contour_lines = None, None
        if contour_mode in ('fillover', 'fill'):
            contour_fill = self.axis.contourf(xi, yi, zi, intervals,
                                              **options)
        if contour_mode != 'fill':
            contour_lines = self.axis.contour(xi, yi, zi, intervals, **options)

        return contour_fill if contour_fill is not None else contour_lines
        # add colorbar somewhere