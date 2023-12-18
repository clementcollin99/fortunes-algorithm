import numpy as np

from .point import Point


class Vertex(Point):
    def __init__(self, coords: tuple, breakpoint=None):
        super().__init__(coords)
        self.breakpoint = breakpoint

    def set_incident_edge(self, incident_edge: "HalfEdge"):
        self.incident_edge = incident_edge

    def get_breakpoint(self):
        return self.breakpoint

    def is_defined(self):
        return not np.isinf(self.as_array()).any()


class HalfEdge:
    def __init__(
        self,
        origin,
        twin: "HalfEdge" = None,
        prev: "HalfEdge" = None,
        next: "HalfEdge" = None,
        incident_face: "Face" = None,
    ):
        self.origin = origin
        self.twin = twin
        self.prev = prev
        self.next = next
        self.incident_face = incident_face
        incident_face.set_outer_component(self)

    def get_origin(self):
        return self.origin

    def get_twin(self):
        return self.twin

    def get_next(self):
        return self.next

    def set_origin(self, origin):
        if origin:
            origin.set_incident_edge(self)
        self.origin = origin

    def set_twin(self, twin):
        if twin:
            twin.twin = self
        self.twin = twin

    def set_next(self, next):
        if next:
            next.prev = self
        self.next = next


class Face:
    def __init__(self, site: Point, outer_component: HalfEdge = None):
        self.site = site
        self.outer_component = outer_component

    def set_outer_component(self, outer_component: HalfEdge):
        if not self.outer_component:
            self.outer_component = outer_component


class Tesselation:
    def __init__(self):
        self.vertices = []
        self.half_edges = []
        self.faces = []

    def plot(self):
        pass
