from pixelsort import util


def lightness(pixel):
    return util.lightness(pixel)


# updated to check inputs
def intensity(pixel):
	if len(pixel) > 3:
		return False
	for num in pixel:
		if not isinstance(num, int):
			return False
	return pixel[0] + pixel[1] + pixel[2]


# updated to check for bad inputs
def maximum(pixel):
	if len(pixel) > 3:
		return False
	for num in pixel:
		if not isinstance(num, int):
			return False
	return max(pixel[0], pixel[1], pixel[2])


# updated to check for bad inputs
def minimum(pixel):
	if len(pixel) > 3:
		return False
	for num in pixel:
		if not isinstance(num, int):
			return False
	return min(pixel[0], pixel[1], pixel[2])
