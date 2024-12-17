import random as rnd
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from pathlib import Path

import computer_text_generator
import background_generator
import distortion_generator


def rotate_bboxes(bboxes, degree, rc):
    """
    旋转文字的边界框 (bounding boxes)。
    """
    def rotate_pts(pts):
        rc, pts = np.array(rc), np.array(pts)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        res = (rc + R @ (pts - rc)).tolist()
        return res

    theta = -degree * np.pi / 180
    res = []
    for bbox in bboxes:
        rc = ((bbox[2][0] + bbox[0][0]) / 2, (bbox[2][1] + bbox[0][1]) / 2)  # 中心点
        rotated_bbox = [rotate_pts(pts) for pts in bbox]
        res.append(rotated_bbox)
    return res


def resize_bboxes(bboxes, ratio, vm, hm):
    """
    调整边界框大小以适应新的图片尺寸。
    """
    res = []
    for bbox in bboxes:
        new_bbox = []
        for pts in bbox:
            new_pts = (int(pts[0] * ratio + hm / 2), int(pts[1] * ratio + vm / 2))
            new_bbox.append(new_pts)
        res.append(new_bbox)
    return res

class FakeTextDataGenerator(object):
    @classmethod
    def generate(cls, index, text, font_list, out_dir, cursive, size, extension, skewing_angle,
                 random_skew, blur, random_blur, background_type, distortion_type, distortion_orientation,
                 is_handwritten, name_format, width, alignment, text_color, orientation, space_width, margins,
                 fit, is_bbox, label_only, bgcolor, strokewidth, strokefill, height=0):
        """
        生成带文本的图像，并保存到指定路径。
        """
        # 解包边距
        margin_top, margin_left, margin_bottom, margin_right = margins
        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        # 生成文字图像及边界框
        image, bboxes = computer_text_generator.generate(
            text, font_list, text_color, size, orientation, space_width, fit, strokewidth, strokefill, cursive
        )

        # 旋转文字图像及边界框
        random_angle = rnd.randint(-skewing_angle, skewing_angle) if random_skew else skewing_angle
        rotated_img = image.rotate(random_angle, expand=1)
        rotated_bboxes = rotate_bboxes(bboxes, random_angle, rotated_img.size)

        # 扭曲效果应用到旋转后的图像
        if distortion_type == 1:  # 正弦波扭曲
            distorted_img = distortion_generator.sin(
                rotated_img, vertical=(distortion_orientation in [0, 2]), horizontal=(distortion_orientation in [1, 2]))
        elif distortion_type == 2:  # 余弦波扭曲
            distorted_img = distortion_generator.cos(
                rotated_img, vertical=(distortion_orientation in [0, 2]), horizontal=(distortion_orientation in [1, 2]))
        elif distortion_type == 3:  # 随机扭曲
            distorted_img = distortion_generator.random(
                rotated_img, vertical=(distortion_orientation in [0, 2]), horizontal=(distortion_orientation in [1, 2]))
        else:
            distorted_img = rotated_img  # 无扭曲

        # 调整文字图像大小
        ratio = (size - vertical_margin) / distorted_img.size[1]
        new_width = int(distorted_img.size[0] * ratio)
        resized_img = distorted_img.resize((new_width, size - vertical_margin), Image.ANTIALIAS)

        # 生成背景图像
        background_width = width if width > 0 else new_width + horizontal_margin
        background_height = size
        if background_type == 0:  # 高斯噪声
            background = background_generator.gaussian_noise(background_height, background_width)
        elif background_type == 1:  # 单一颜色
            background = background_generator.plain_color(background_height, background_width, bgcolor)
        elif background_type == 2:  # 准晶背景
            background = background_generator.quasicrystal(background_height, background_width)
        else:  # 随机图片背景
            background = background_generator.picture(background_height, background_width)

        # 将文字图像贴到背景上
        text_position = (margin_left, margin_top)
        background.paste(resized_img, text_position, resized_img)

        # 截取文字区域
        crop_left = text_position[0] - margin_left
        crop_top = text_position[1] - margin_top
        crop_right = crop_left + new_width + horizontal_margin
        crop_bottom = crop_top + size
        cropped_img = background.crop((crop_left, crop_top, crop_right, crop_bottom))

        # 如果指定高度，调整图像大小
        if height > 0:
            target_width = int(cropped_img.width * (height / cropped_img.height))
            cropped_img = cropped_img.resize((target_width, height), Image.ANTIALIAS)

        # 应用模糊效果
        if blur > 0:
            cropped_img = cropped_img.filter(ImageFilter.GaussianBlur(radius=blur))

        # 保存图像
        image_name = f"{str(index).zfill(6)}.{extension}"
        cropped_img.convert('RGB').save(Path(out_dir) / image_name)