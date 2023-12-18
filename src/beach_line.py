import numpy as np

from .point import Point
from .tesselation import HalfEdge
from .equations import get_y_parabola
from .geom_utils import get_intersection


class Node:
    def __init__(
        self,
        parent: "Node" = None,
        child_side: str = None,
        left: "Node" = None,
        right: "Node" = None,
    ):
        self.parent = parent
        self.child_side = child_side
        self.left = left
        self.right = right
        left.set_parent(self, "left") if left else None
        right.set_parent(self, "right") if right else None

    def set_parent(self, parent: "Node", child_side: str):
        self.parent = parent
        self.child_side = child_side

    def set_left_child(self, left: "Node"):
        self.left = left

    def set_right_child(self, right: "Node"):
        self.right = right

    @staticmethod
    def get_key(self, y_sweep_line: float = None):
        pass


class Arc(Node):
    def __init__(
        self,
        focus: Point,
        parent: Node = None,
        child_side: str = None,
        left: Node = None,
        right: Node = None,
    ):
        super().__init__(parent, child_side, left, right)
        self.focus = focus
        self.event = None

    def set_event(self, event):
        self.event = event

    def get_plot(self, x, y_sweep_line: float):
        if self.focus.y - y_sweep_line == 0:
            return

        return list(eval(get_y_parabola))

    def get_key(self, y_sweep_line: float = None):
        return self.focus.x


class BreakPoint(Node):
    def __init__(
        self,
        parent=None,
        child_side=None,
        left=None,
        right=None,
        half_edge: HalfEdge = None,
    ):
        super().__init__(parent, child_side, left, right)
        self.half_edge = half_edge

    def set_half_edge(self, half_edge: HalfEdge):
        self.half_edge = half_edge

    def get_left_arc(self):
        def _recursive(node):
            if isinstance(node, Arc):
                return node

            if node.right:
                return _recursive(node.right)

            return _recursive(node.left)

        return _recursive(self.left)

    def get_right_arc(self):
        def _recursive(node):
            if isinstance(node, Arc):
                return node

            if node.left:
                return _recursive(node.left)

            return _recursive(node.right)

        return _recursive(self.right)

    def get_coords(self, y_sweep_line: int):
        left_arc = self.get_left_arc()
        right_arc = self.get_right_arc()

        x_p0, y_p0, x_p1, y_p1 = (
            left_arc.focus.x,
            left_arc.focus.y,
            right_arc.focus.x,
            right_arc.focus.y,
        )

        if y_p0 == y_sweep_line:
            return x_p0

        if y_p1 == y_sweep_line:
            return x_p1

        return get_intersection(self, y_sweep_line)

    def get_key(self, y_sweep_line: float = None):
        if not y_sweep_line:
            raise ValueError("Missing parameter @y_sweep_line!")

        return self.get_coords(y_sweep_line).x


class BeachLine:
    def __init__(self, root: Arc | BreakPoint = None):
        self.root = root

    def is_empty(self):
        return not self.root

    def get_arcs_ordered(self):
        def _recursive(node, arcs):
            if not node:
                return

            _recursive(node.left, arcs)

            if isinstance(node, Arc):
                arcs.append(node)

            _recursive(node.right, arcs)

            return arcs

        arcs = list()
        _recursive(self.root, arcs)

        return arcs

    def get_nodes_ordered(self):
        def _recursive(node, nodes):
            if not node:
                return

            _recursive(node.left, nodes)
            nodes.append(node)
            _recursive(node.right, nodes)

            return nodes

        nodes = list()
        _recursive(self.root, nodes)

        return nodes

    def get_three_consecutive_arcs(self, arc: Arc, reverse: bool = False):
        arcs = self.get_arcs_ordered()

        if not arcs:
            return

        try:
            pos = next(filter(lambda x: id(x[1]) == id(arc), enumerate(arcs)))[0]
        except (StopIteration, IndexError):
            print("Arc not found!")
            return

        consecutive_arcs = (
            arcs[np.max((0, pos - 2)) : np.min((len(arcs), pos + 1))]
            if reverse
            else arcs[pos : np.min((len(arcs), pos + 3))]
        )

        if len(consecutive_arcs) == 3:
            return consecutive_arcs

        return

    def get_surrounding_breakpoints(self, arc: Arc):
        nodes = self.get_nodes_ordered()
        pos = next(filter(lambda x: id(x[1]) == id(arc), enumerate(nodes)))[0]
        return nodes[pos - 1], nodes[pos + 1]

    def delete(self, arc: Arc):
        left_bp, right_bp = self.get_surrounding_breakpoints(arc)
        setattr(arc.parent, arc.child_side, None)
        opposite_side = "right" if arc.child_side == "left" else "left"
        setattr(
            arc.parent.parent,
            arc.parent.child_side,
            getattr(arc.parent, opposite_side),
        )

        removed = right_bp if opposite_side == "right" else left_bp
        updated = right_bp if opposite_side == "left" else left_bp

        del arc
        return left_bp, right_bp, removed, updated

    def rebalance(self):
        nodes = self.get_nodes_ordered()

        def _recursive(nodes, parent: BreakPoint = None, child_side: str = None):
            if not nodes:
                return

            mid = len(nodes) // 2
            node = nodes[mid]

            node.set_parent(parent, child_side)
            node.left = _recursive(nodes[:mid], node, "left")
            node.right = _recursive(nodes[mid + 1 :], node, "right")

            return node

        self.root = _recursive(nodes)

    def search(
        self,
        x: float,
        y_sweep_line: float,
        parent: Arc | BreakPoint = None,
        child_side: str = None,
        node: Arc | BreakPoint = None,
    ):
        if not node:
            node = self.root

        if isinstance(node, Arc):
            return child_side, parent, node

        if node.get_key(y_sweep_line) > x:
            return self.search(x, y_sweep_line, node, "left", node.left)

        return self.search(x, y_sweep_line, node, "right", node.right)
