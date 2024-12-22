import cv2
import math
import os
import random as rnd
import numpy as np

from PIL import Image, ImageDraw, ImageFilter

def gaussian_noise(height, width):
    """
        Create a background with Gaussian noise (to mimic paper)
    """

    # We create an all white image
    image = np.ones((height, width)) * 255

    # We add gaussian noise
    cv2.randn(image, 235, 10)

    return Image.fromarray(image).convert('RGBA')

def plain_color(height, width, bgcolor):
    """
        Create a plain white background
    """
    ### create color background 363636 cfb202
    img = Image.new(mode="RGB", size=(width,height), color=bgcolor)
    return img.convert('RGBA')
    # return Image.new("L", (width, height), 255).convert('RGBA')


def quasicrystal(height, width):
    """
        Create a background with quasicrystal (https://en.wikipedia.org/wiki/Quasicrystal)
    """

    image = Image.new("L", (width, height))
    pixels = image.load()

    frequency = rnd.random() * 30 + 20 # frequency
    phase = rnd.random() * 2 * math.pi # phase
    rotation_count = rnd.randint(10, 20) # of rotations

    for kw in range(width):
        y = float(kw) / (width - 1) * 4 * math.pi - 2 * math.pi
        for kh in range(height):
            x = float(kh) / (height - 1) * 4 * math.pi - 2 * math.pi
            z = 0.0
            for i in range(rotation_count):
                r = math.hypot(x, y)
                a = math.atan2(y, x) + i * math.pi * 2.0 / rotation_count
                z += math.cos(r * math.sin(a) * frequency + phase)
            c = int(255 - round(255 * z / rotation_count))
            pixels[kw, kh] = c # grayscale
    return image.convert('RGBA')

def picture(height, width):
    """
    Create a background with a picture
    """
    bg = os.listdir('./bg')

    if len(bg) > 0:
        pic = Image.open('./bg/' + bg[rnd.randint(0, len(bg) - 1)])

        if pic.size[0] < width:
            pic = pic.resize([width, int(pic.size[1] * (width / pic.size[0]))], Image.ANTIALIAS)

        elif pic.size[1] < height:
            pic = pic.thumbnail([int(pic.size[0] * (height / pic.size[1])), height], Image.ANTIALIAS)

        # 如果缩放后的图片宽度等于目标宽度，裁剪的起始点 x 为 0。
        if (pic.size[0] == width):
            x = 0
        else:
            x = rnd.randint(0, pic.size[0] - width)

        # 如果缩放后的图片高度等于目标高度，裁剪的起始点 y 为 0。
        if (pic.size[1] == height):
            y = 0
        else:
            y = rnd.randint(0, pic.size[1] - height)

        return pic.crop(
            (
                x,
                y,
                x + width,
                y + height,
            )
        )
        # 按照计算出的起始点 (x, y) 和目标尺寸 (width, height) 对图片进行裁剪并返回裁剪后的图片。

    else:
        raise Exception('No images where found in the pictures folder!')
        # 如果 bg 文件夹中没有图片文件，则抛出异常提示用户。