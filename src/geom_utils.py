import numpy as np

from .point import Point
from .tesselation import Vertex

OFFSET = 10


def get_y_parabola(x: float, focus: Point, y_sweep_line: float):
    return list(
        (x**2 - 2 * focus.x * x + focus.x**2 + focus.y**2 - y_sweep_line**2)
        / (2 * (focus.y - y_sweep_line))
    )


def get_intersection(breakpoint, y_sweep_line: float, max_y: float = None):
    i, j = breakpoint.get_left_arc().focus, breakpoint.get_right_arc().focus
    l = y_sweep_line

    result = Point((np.inf, np.inf))
    p = i

    a = i.x
    b = i.y
    c = j.x
    d = j.y
    u = 2 * (b - l)
    v = 2 * (d - l)

    if i.y == j.y:
        result.x = (i.x + j.x) / 2

        if j.x < i.x:
            result.y = max_y or float("inf")
            return result

    elif i.y == l:
        result.x = i.x

        p = j
    elif j.y == l:
        result.x = j.x

    else:
        x = -(
            np.sqrt(
                v * (a**2 * u - 2 * a * c * u + b**2 * (u - v) + c**2 * u)
                + d**2 * u * (v - u)
                + l**2 * (u - v) ** 2
            )
            + a * v
            - c * u
        ) / (u - v)
        result.x = x

    a = p.x
    b = p.y
    x = result.x
    u = 2 * (b - l)

    if u == 0:
        result.y = float("inf")
        return result

    result.y = 1 / u * (x**2 - 2 * a * x + a**2 + b**2 - l**2)

    return result


def calculate_angle(point, center):
    dx = point.x - center.x
    dy = point.y - center.y
    return np.math.degrees(np.math.atan2(dy, dx)) % 360


def check_clockwise(a, b, c, center):
    angle_1 = calculate_angle(a, center)
    angle_2 = calculate_angle(b, center)
    angle_3 = calculate_angle(c, center)

    counter_clockwise = (angle_3 - angle_1) % 360 > (angle_3 - angle_2) % 360

    if counter_clockwise:
        return False

    return True


def _finish_edge(edge, bounding_box):
    starts = edge.get_origin().is_defined()
    ends = edge.twin.get_origin().is_defined()

    if starts and ends:
        return

    breakpoint = edge.get_origin().get_breakpoint()
    edge.set_origin(
        Vertex(breakpoint.get_coords(bounding_box.y_min - OFFSET))
    ) if not starts and breakpoint else np.nan

    breakpoint = edge.twin.get_origin().get_breakpoint()
    edge.set_origin(
        Vertex(breakpoint.get_coords(bounding_box.y_min - OFFSET))
    ) if not ends and breakpoint else np.nan

    return


def finish_edges(edges, bounding_box):
    for edge in edges.copy():
        if not edge.get_origin().is_defined() or not bounding_box.contains(
            [edge.get_origin()]
        ):
            _finish_edge(edge, bounding_box)

        # if (
        #     not edge.get_origin().is_defined()
        #     or not edge.twin.get_origin().is_defined()
        # ):
        #     edges.remove(edge)
        #     edges.remove(edge.twin)
