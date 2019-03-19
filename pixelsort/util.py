import random
import string
from colorsys import rgb_to_hsv


def id_generator(size=5, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def lightness(pixel):
    return rgb_to_hsv(pixel[0], pixel[1], pixel[2])[2] / 255.0  # For backwards compatibility with python2


# Updated to check for bad input
def random_width(clength):
    # check if input is an integer
    if not isinstance(clength, int):
        return False
    # if integer is negative, return false
    if clength < 0:
        return False

    # get a random number
    x = random.random()

    # set width equal a value less than or equal to clength
    width = int(clength * (1 - x))
    return width


def crop_to(image_to_crop, reference_image):
    """
    Crops image to the size of a reference image. This function assumes that the relevant image is located in the center
    and you want to crop away equal sizes on both the left and right as well on both the top and bottom.
    :param image_to_crop
    :param reference_image
    :return: image cropped to the size of the reference image
    """
    reference_size = reference_image.size
    current_size = image_to_crop.size
    dx = current_size[0] - reference_size[0]
    dy = current_size[1] - reference_size[1]
    left = dx / 2
    upper = dy / 2
    right = dx / 2 + reference_size[0]
    lower = dy / 2 + reference_size[1]
    return image_to_crop.crop(box=(left, upper, right, lower))
