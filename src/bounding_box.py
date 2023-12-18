import numpy as np

from .point import Point


class BoundingBox:
    def __init__(self, sites, offset=2):
        self.x_min = min([site.x for site in sites]) - offset
        self.x_max = max([site.x for site in sites]) + offset
        self.y_min = min([site.y for site in sites]) - offset
        self.y_max = max([site.y for site in sites]) + offset

    def get_coordinates(self):
        return [
            [self.x_min, self.y_min],
            [self.x_max, self.y_min],
            [self.x_max, self.y_max],
            [self.x_min, self.y_max],
        ]

    def contains(self, points: list):
        return np.all(
            [
                point.x > self.x_min
                and point.x < self.x_max
                and point.y > self.y_min
                and point.y < self.y_max
                for point in points
            ]
        )
