import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

from matplotlib import patches
from .event_queue import CircleEvent


class Colors:
    sweep_line = "#2c3e50"
    vertices = "#34495e"
    beach_line = "#f1c40f"
    edge = "#636e72"
    arc = "#95a5a6"
    invalid_circle = "#ecf0f1"
    valid_circle = "#2980b9"
    sites = "#bdc3c7"
    bounding_box = "black"


class Visualizer:
    def __init__(
        self, voronoi, bounding_box, offset=2, figsize=(8, 8), save_dir="images"
    ):
        """
        A useful class to visualize the Fortune's algorithm execution
        and the resulting Voronoi tesselation.
        """
        self.voronoi = voronoi
        self.bounding_box = bounding_box
        self.offset = offset
        self.figsize = figsize
        self.save_dir = save_dir

        self.x_min, self.x_max, self.y_min, self.y_max = self.canvas_size(
            bounding_box, offset
        )

        plt.close("all")
        _, self.canvas = plt.subplots(figsize=figsize)
        self.set_limits()

        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(save_dir)

    @staticmethod
    def canvas_size(bounding_box, offset: int):
        """
        Get the limits of the canvas.
        """
        x_min = bounding_box.x_min - offset
        x_max = bounding_box.x_max + offset
        y_min = bounding_box.y_min - offset
        y_max = bounding_box.y_max + offset

        # make it a square
        x_min = y_min = min(x_min, y_min)
        x_max = y_max = min(x_max, y_max)

        return x_min, x_max, y_min, y_max

    def set_limits(self):
        """
        Set the limits of the canvas.
        """
        self.canvas.set_ylim(self.y_min, self.y_max)
        self.canvas.set_xlim(self.x_min, self.x_max)
        return

    def plot_bounding_box(self):
        """
        Plot the outline.
        """
        poly = patches.Polygon(
            self.bounding_box.get_coordinates(),
            fill=False,
            edgecolor=Colors.bounding_box,
        )

        self.canvas.add_patch(poly)
        return

    def plot_vertices(
        self,
        vertices: list = None,
        color: str = Colors.vertices,
        zorder: int = 10,
        **kwargs,
    ):
        """
        Display the vertices.
        """
        vertices = vertices or self.voronoi.vertices

        xs = [vertex.x for vertex in vertices]
        ys = [vertex.y for vertex in vertices]

        self.canvas.scatter(xs, ys, s=50, color=color, zorder=zorder, **kwargs)

        return

    def plot_sites(
        self,
        sites: list = None,
        color: str = Colors.sites,
        zorder: int = 10,
        **kwargs,
    ):
        """
        Plot the sites.
        """
        points = sites or self.voronoi.sites

        xs = [point.x for point in points]
        ys = [point.y for point in points]

        self.canvas.scatter(xs, ys, s=50, color=color, zorder=zorder, **kwargs)

        return

    def plot_edge(self, edge, color=Colors.edge):
        if not (edge and edge.twin):
            return

        start, end = edge.origin, edge.twin.origin
        x_range = [start.x, end.x]
        y_range = [start.y, end.y]
        self.canvas.plot(x_range, y_range, color)

        return

    def plot_edges(self, edges: list = None, color: str = Colors.edge, **kwargs):
        """
        Plot the borders of the cells.
        """
        for edge in edges:
            self.plot_edge(edge, color=color)
            self.plot_edge(edge.twin, color=color)

        return

    def plot_arcs(self, arcs: list, y_sweep_line: float, n_points: int = 1000):
        """
        Plot the arcs.
        """
        x = np.linspace(float(self.x_min), float(self.x_max), n_points)
        arc_plots = []

        for arc in arcs:
            arc_plot = arc.get_plot(x, y_sweep_line)
            if arc_plot:
                self.canvas.plot(x, arc_plot, linestyle="--", color=Colors.arc)
                arc_plots.append(arc_plot)

        # beach_line
        if arc_plots:
            bottom = np.min(arc_plots, axis=0)
            self.canvas.plot(x, bottom, color=Colors.beach_line)

        return

    def plot_sweep_line(self, y_sweep_line: float):
        """
        Plot the sweep line.
        """
        if not y_sweep_line:
            return

        x_range = [self.x_min, self.x_max]
        y_range = [y_sweep_line, y_sweep_line]
        self.canvas.plot(x_range, y_range, color=Colors.sweep_line)

        return

    def plot_circle(
        self,
        x: float,
        y: float,
        radius: float,
        is_valid: bool = True,
        plot_center: bool = True,
    ):
        """
        Plot a circle.
        """
        color = Colors.valid_circle if is_valid else Colors.invalid_circle
        circle = plt.Circle((x, y), radius, fill=False, color=color, linewidth=2)
        self.canvas.add_artist(circle)

        if plot_center:
            self.canvas.scatter(x, y, s=50, color=color)

        return

    def plot_circle_event(self, event):
        """
        Plot the circle of a circle event.
        """
        if isinstance(event, CircleEvent):
            self.plot_circle(event.point.x, event.point.y, event.radius, event.is_valid)

        return

    def plot(
        self,
        edges: list = None,
        vertices: list = None,
        sites: list = None,
        arcs: list = None,
        y_sweep_line: float = None,
        event: CircleEvent = None,
        fig_name: str = None,
    ):
        """
        Convenient method to display sevral components.
        """
        plt.close("all")
        _, self.canvas = plt.subplots(figsize=self.figsize)
        self.set_limits()

        plt.xticks([])
        plt.yticks([])
        plt.tight_layout()

        self.plot_sweep_line(y_sweep_line) if y_sweep_line else np.nan
        self.plot_edges(edges) if edges else np.nan
        self.plot_vertices(vertices) if vertices else np.nan
        self.plot_sites(sites) if sites else np.nan
        self.plot_arcs(arcs, y_sweep_line) if arcs and y_sweep_line else np.nan
        self.plot_circle_event(event) if event and isinstance(
            event, CircleEvent
        ) else np.nan

        path = os.path.join(self.save_dir, f"{fig_name}.png")
        plt.savefig(path) if fig_name else np.nan

        return
