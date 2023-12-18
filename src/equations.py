get_y_parabola = """ (
    x**2
    - 2 * self.focus.x * x
    + self.focus.x**2
    + self.focus.y**2
    - y_sweep_line**2
) / (2 * (self.focus.y - y_sweep_line))
"""
