import random

def sort_image(pixels, intervals, randomness, s_func):
    sorted_pixels = []
    for y in range(len(pixels)):
        row = []
        x_min = 0
        for x_max in intervals[y]:
            interval = []
            for x in range(x_min, x_max):
                interval.append(pixels[y][x])
            if random.randint(0, 100) >= randomness:
                row += sort_interval(interval, s_func)
            else:
                row += interval
            x_min = x_max
        row.append(pixels[y][0])
        sorted_pixels.append(row)
    return sorted_pixels


def sort_interval(interval, sorting_function):
    return [] if interval == [] else sorted(interval, key=sorting_function)
