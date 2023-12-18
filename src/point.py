import numpy as np


class Point:
    def __init__(self, coords):
        if isinstance(coords, Point):
            self.x = coords.x
            self.y = coords.y
            return

        self.x = coords[0]
        self.y = coords[1]

    def translate(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y

    def as_array(self):
        return np.array([self.x, self.y])

    def dist(self, p):
        return np.linalg.norm(self.as_array() - p.as_array())

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, point: "Point"):
        return self.x == point.x and self.y == point.y
