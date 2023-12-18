import numpy as np


class SweepLine:
    def __init__(self, height: float = np.nan):
        self.height = height

    def set_height(self, height: float):
        self.height = height

    def get_height(self):
        return self.height
