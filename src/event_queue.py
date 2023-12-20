import numpy as np

from queue import PriorityQueue
from abc import ABC, abstractmethod

from .bounding_box import BoundingBox
from .point import Point
from .beach_line import Arc, BreakPoint, BeachLine
from .tesselation import Vertex, HalfEdge, Tesselation
from .sweep_line import SweepLine
from .geom_utils import check_clockwise


class Event(ABC):
    def __init__(
        self,
        point: Point,
        event_queue: "EventQueue",
        voronoi: Tesselation,
        beach_line: BeachLine,
        sweep_line: SweepLine,
        bounding_box: BoundingBox,
    ):
        self.point = point
        self.event_queue = event_queue
        self.voronoi = voronoi
        self.beach_line = beach_line
        self.sweep_line = sweep_line
        self.bounding_box = bounding_box
        self.is_valid = True

    @property
    def x(self):
        return np.inf

    @property
    def y(self):
        return np.inf

    def __lt__(self, other):
        if self == other:
            return isinstance(self, CircleEvent) and not isinstance(other, CircleEvent)

        if self.y == other.y:
            return self.x < other.x

        return self.y > other.y

    def __eq__(self, other):
        if not other:
            return

        return self.y == other.y and self.x == other.x

    def __ne__(self, other):
        return not self.__eq__(other)

    def look_for_circle_event(self, arc: Arc, reverse: bool = False):
        arcs = self.beach_line.get_three_consecutive_arcs(arc, reverse)

        if not arcs:
            return

        predecessor, arc, successor = arcs
        a, b, c = predecessor.focus, arc.focus, successor.focus

        tmp_1 = 2 * ((b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x))

        if tmp_1 == 0:  # the points belong to one line, so no circle can be traced
            return

        tmp_2 = (b.x - a.x) * (a.x + b.x) + (b.y - a.y) * (a.y + b.y)
        tmp_3 = (c.x - a.x) * (a.x + c.x) + (c.y - a.y) * (a.y + c.y)

        # center and radius of the circle
        x = ((c.y - a.y) * tmp_2 - (b.y - a.y) * tmp_3) / tmp_1
        y = ((b.x - a.x) * tmp_3 - (c.x - a.x) * tmp_2) / tmp_1
        point = Point((x, y))

        if not self.bounding_box.contains([point]):
            return

        if not check_clockwise(a, b, c, point):
            return

        radius = np.sqrt((a.x - x) ** 2 + (a.y - y) ** 2)

        circle_event = CircleEvent(
            point,
            self.event_queue,
            self.voronoi,
            self.beach_line,
            self.sweep_line,
            self.bounding_box,
            arc,
            predecessor,
            successor,
            radius,
        )
        self.event_queue.put(circle_event)
        arc.set_event(circle_event)

        return

    @abstractmethod
    def handle(self):
        pass


class SiteEvent(Event):
    def __init__(
        self,
        point: Point,
        event_queue: "EventQueue",
        voronoi: Tesselation,
        beach_line: BeachLine,
        sweep_line: SweepLine,
        bounding_box: BoundingBox,
    ):
        super().__init__(
            point,
            event_queue,
            voronoi,
            beach_line,
            sweep_line,
            bounding_box,
        )

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def handle(self):
        # first, update the height of the sweep line
        self.sweep_line.set_height(self.point.y)

        if self.beach_line.is_empty():  # 1.
            self.beach_line.root = Arc(self.point)
            return

        # 2.
        parent_side, parent, splitted_arc = self.beach_line.search(
            self.point.x, y_sweep_line=self.point.y
        )

        if isinstance(splitted_arc.event, CircleEvent):
            splitted_arc.event.remove()  # false alarm

        # 3.
        arc_1 = Arc(splitted_arc.focus)
        arc_2 = Arc(self.point)
        arc_3 = Arc(splitted_arc.focus)
        right_bp = BreakPoint(left=arc_2, right=arc_3)
        left_bp = BreakPoint(parent, parent_side, arc_1, right_bp)

        # 4.
        filter_1 = lambda x: x.site == splitted_arc.focus
        filter_2 = lambda x: x.site == self.point

        he_1 = HalfEdge(
            Vertex((np.inf, np.inf), breakpoint=right_bp),
            incident_face=next(filter(filter_1, self.voronoi.faces)),
        )

        he_2 = HalfEdge(
            Vertex((np.inf, np.inf), breakpoint=left_bp),
            twin=he_1,
            incident_face=next(filter(filter_2, self.voronoi.faces)),
        )

        he_1.set_twin(he_2)
        self.voronoi.half_edges.extend((he_1, he_2))

        right_bp.set_half_edge(he_1)
        left_bp.set_half_edge(he_2)

        if parent:
            setattr(left_bp.parent, parent_side, left_bp)
        else:
            self.beach_line.root = left_bp

        # rebalance the BeachLine
        self.beach_line.balance_and_propagate(left_bp)

        # free some space
        del splitted_arc.event, splitted_arc

        # 5. look for new circle events
        self.look_for_circle_event(arc_2, reverse=False)
        self.look_for_circle_event(arc_2, reverse=True)


class CircleEvent(Event):
    def __init__(
        self,
        point: Point,
        event_queue: "EventQueue",
        voronoi: Tesselation,
        beach_line: BeachLine,
        sweep_line: SweepLine,
        bounding_box: BoundingBox,
        arc: Arc,
        predecessor: Arc,
        successor: Arc,
        radius: float,
    ):
        super().__init__(
            point,
            event_queue,
            voronoi,
            beach_line,
            sweep_line,
            bounding_box,
        )
        self.arc = arc
        self.predecessor = predecessor
        self.successor = successor
        self.radius = radius

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y - self.radius

    def remove(self):
        self.is_valid = False
        return

    def handle(self):
        # if the event has been removed, skip
        if not self.is_valid:
            return

        # first, update the height of the sweep line
        self.sweep_line.set_height(self.point.y - self.radius)

        # delete all circle events involving self.arc
        self.predecessor.event.remove() if self.predecessor.event else np.nan
        self.successor.event.remove() if self.successor.event else np.nan

        # delete self.arc from the binary search tree
        left_bp, right_bp, removed, updated = self.beach_line.delete(self.arc)

        # 2.
        vertex = Vertex(self.point.as_array())
        self.voronoi.vertices.append(vertex)

        left_bp.half_edge.origin = vertex
        right_bp.half_edge.origin = vertex

        filter_1 = lambda x: x.site == updated.get_left_arc().focus
        filter_2 = lambda x: x.site == updated.get_right_arc().focus

        he_1 = HalfEdge(
            vertex,
            incident_face=next(filter(filter_1, self.voronoi.faces)),
        )
        he_2 = HalfEdge(
            Vertex((np.inf, np.inf), breakpoint=updated),
            twin=he_1,
            incident_face=next(filter(filter_2, self.voronoi.faces)),
        )
        he_1.set_twin(he_2)
        self.voronoi.half_edges.extend((he_1, he_2))

        # set half_edges' next
        left_bp.half_edge.twin.set_next(he_1)
        right_bp.half_edge.twin.set_next(left_bp.half_edge)
        he_1.twin.set_next(right_bp.half_edge)

        del removed

        updated.set_half_edge(he_2)

        # 3. look for new circle events
        self.look_for_circle_event(updated.get_left_arc(), reverse=False)
        self.look_for_circle_event(updated.get_right_arc(), reverse=True)


class EventQueue:
    def __init__(self):
        self.queue = PriorityQueue()

    def put(self, event: Event):
        self.queue.put(event)

    def get(self) -> Event:
        return self.queue.get()

    def is_empty(self):
        return self.queue.empty()

    def __str__(self):
        return "\n".join([str(event) for event in self.queue])
