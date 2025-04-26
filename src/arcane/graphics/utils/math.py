import numpy as np


def avoid_zero(num):
    if num == 0:
        return 0.001
    else:
        return num


def compute_function_range(func, value_range, num_samples=100):
    x_values = np.linspace(value_range[0], value_range[1], num_samples)
    vfunc = np.vectorize(func)
    y_values = vfunc(x_values)
    y_min, y_max = np.min(y_values), np.max(y_values)
    return [y_min, y_max]
