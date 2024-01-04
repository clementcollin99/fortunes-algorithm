from .point import Point
from .bounding_box import BoundingBox
from .beach_line import BeachLine
from .event_queue import SiteEvent, CircleEvent, EventQueue
from .tesselation import Tesselation, Face
from .visualizer import Visualizer
from .sweep_line import SweepLine
from .geom_utils import finish_edges


class Fortune:
    def __init__(self, sites: list):
        self.sites = [Point(site) for site in sites]
        self.sites.sort(key=lambda p: p.y)

        # create a bounding box around the sites
        self.bounding_box = BoundingBox(self.sites)

        # create the beach line
        self.beach_line = BeachLine()

        # create the data structure to store the Voronoi diagram
        self.voronoi = Tesselation()
        self.voronoi.faces = [Face(site) for site in self.sites]

        # create an object that handles the visualisation
        self.visualizer = Visualizer(self.voronoi, self.bounding_box)
        self.sweep_line = SweepLine(self.visualizer.y_max)

        # create the queue of events
        self.event_queue = EventQueue()

        # records of valid circle events
        self.past_events = []

        # enqueue the "site events" to come
        for site in self.sites:
            self.event_queue.put(
                SiteEvent(
                    site,
                    self.event_queue,
                    self.voronoi,
                    self.beach_line,
                    self.sweep_line,
                    self.bounding_box,
                    self.past_events,
                )
            )

    def launch(self):
        i = 1
        while not self.event_queue.is_empty():
            event = self.event_queue.get()
            event.handle()

            self.visualizer.plot(
                edges=self.voronoi.half_edges,
                vertices=self.voronoi.vertices,
                sites=self.sites,
                arcs=self.beach_line.get_arcs_ordered(),
                y_sweep_line=self.sweep_line.get_height(),
                event=event,
                fig_name=f"step_{i}",
            )

            i += 1

        # define incomplete edges
        finish_edges(self.voronoi.half_edges, self.bounding_box)

        # plot final result
        self.visualizer.plot(
            edges=self.voronoi.half_edges,
            vertices=self.voronoi.vertices,
            sites=self.sites,
            fig_name=f"step_{i}",
        )

        self.visualizer.plot(
            edges=self.voronoi.half_edges,
            sites=self.sites,
            fig_name=f"step_{i+1}",
        )

        # solve the largest circle problem and plot the solution
        self.visualizer.plot(
            edges=self.voronoi.half_edges,
            sites=self.sites,
            event=max(self.past_events, key=lambda x: x.radius),
            fig_name=f"largest_circle",
        )
