import numpy as np

from .point import Point
from .tesselation import Vertex

OFFSET = 10


def get_y_parabola(x: float, focus: Point, y_sweep_line: float):
    return list(
        (x**2 - 2 * focus.x * x + focus.x**2 + focus.y**2 - y_sweep_line**2) /
        (2 * (focus.y - y_sweep_line)))


def get_intersection(breakpoint, y_sweep_line: float, max_y: float = None):
    i = breakpoint.get_left_arc().focus
    j = breakpoint.get_right_arc().focus
    result = Point((np.inf, np.inf))

    s = y_sweep_line
    p = i
    u = 2 * (i.y - s)
    v = 2 * (j.y - s)

    if i.y == j.y:
        result.x = (i.x + j.x) / 2

        if j.x < i.x:
            result.y = max_y or float("inf")
            return result

    elif i.y == s:
        result.x = i.x
        p = j

    elif j.y == s:
        result.x = j.x

    else:
        x = -(np.sqrt(v * (i.x**2 * u - 2 * i.x * j.x * u + i.y**2 *
                           (u - v) + j.x**2 * u) + j.y**2 * u *
                      (v - u) + s**2 *
                      (u - v)**2) + i.x * v - j.x * u) / (u - v)
        result.x = x

    i.x = p.x
    i.y = p.y
    x = result.x
    u = 2 * (i.y - s)

    if u == 0:
        result.y = float("inf")
        return result

    result.y = 1 / u * (x**2 - 2 * i.x * x + i.x**2 + i.y**2 - s**2)

    return result


def calculate_angle(point, center):
    dx = point.x - center.x
    dy = point.y - center.y
    return np.math.degrees(np.math.atan2(dy, dx)) % 360


def check_clockwise(x, y, z, center):
    angle_1 = calculate_angle(x, center)
    angle_2 = calculate_angle(y, center)
    angle_3 = calculate_angle(z, center)

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
    edge.set_origin(Vertex(breakpoint.get_coords(
        bounding_box.y_min - OFFSET))) if not starts and breakpoint else np.nan

    breakpoint = edge.twin.get_origin().get_breakpoint()
    edge.set_origin(Vertex(
        breakpoint.get_coords(bounding_box.y_min -
                              OFFSET))) if not ends and breakpoint else np.nan

    return


def finish_edges(edges, bounding_box):
    for edge in edges.copy():
        if not edge.get_origin().is_defined() or not bounding_box.contains(
            [edge.get_origin()]):
            _finish_edge(edge, bounding_box)
