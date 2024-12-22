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
    如不需要字符级别 bbox，可忽略此函数。
    """
    def rotate_pts(pts):
        # 根据中心点 rc 和旋转矩阵 R，旋转点坐标
        rc_arr, pts_arr = np.array(rc), np.array(pts)
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        return (rc_arr + R @ (pts_arr - rc_arr)).tolist()

    theta = -degree * np.pi / 180
    res = []
    for bbox in bboxes:
        # 这里写的是以 bbox 的对角点来算中心，如只关心整行，可自行修改
        rc = ((bbox[2][0] + bbox[0][0]) / 2, 
              (bbox[2][1] + bbox[0][1]) / 2)
        rotated_bbox = [rotate_pts(pt) for pt in bbox]
        res.append(rotated_bbox)
    return res


def resize_bboxes(bboxes, ratio, vm, hm):
    """
    调整边界框大小以适应新的图片尺寸。如果无需字符坐标，可忽略此函数。
    ratio: 缩放比
    vm: 垂直方向总边距 (top + bottom)
    hm: 水平方向总边距 (left + right)
    """
    res = []
    for bbox in bboxes:
        new_bbox = []
        for pts in bbox:
            new_x = int(pts[0] * ratio + hm / 2)
            new_y = int(pts[1] * ratio + vm / 2)
            new_bbox.append((new_x, new_y))
        res.append(new_bbox)
    return res


class FakeTextDataGenerator:
    @classmethod
    def generate(
        cls,
        index,
        text,
        font_list,
        out_dir,
        cursive,
        size,                  # 期望的图像/文字参考高度；若 height=0，实际生成图像高度 = size
        extension,
        skewing_angle,
        random_skew,
        blur,
        background_type,
        distortion_type,
        distortion_orientation,
        width,                 # 期望的最终图像宽度（<=0则自适应文字宽）
        text_color,
        orientation,
        space_width,
        margins,               # "top,left,bottom,right"
        fit,
        bgcolor,
        stroke_width,
        stroke_fill,
        label_path,
        height=0               # 若>0，则最终图像高度 = height
    ):
        """
        生成带文本的图像，并保存到指定路径；不关心单个字符 bbox。
        
        主要流程：
         1) 使用 computer_text_generator.generate(...) 生成文字图
         2) 创建背景图
         3) 随机在背景图内贴文字图
         4) 旋转 (random_skew) + distort (扭曲) + resize + blur
         5) 保存图像并记录 label.txt
        """

        # ----0. 解析边距----
        margin_top, margin_left, margin_bottom, margin_right = map(int, margins.split(','))
        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        # ----1. 生成文字图 (整行)----
        #  computer_text_generator.generate 返回 (text_img, box_info)
        text_img, _ = computer_text_generator.generate(
            text=text,
            font_list=font_list,
            text_color=text_color,
            font_size=size,
            orientation=orientation,
            space_width=space_width,
            fit=fit,
            strokewidth=stroke_width,
            strokefill=stroke_fill,
            cursive=cursive
        )

        # 如果文字图是空图，则直接返回
        if text_img.size == (1, 1):
            return None, None

        # 调试-保存文字图
        print("text_img.size =", text_img.size)
        text_img.save("debug_text_img.png")
        
        # ----2. 生成背景----
        #  背景高度默认是 size。如果文字图比 size 还高，就自适应
        bg_h = max(size, text_img.height + vertical_margin)
        bg_w = text_img.width + horizontal_margin

        # 创建对应类型的背景
        # if background_type == 0:  # 高斯噪声
        #     background_img = background_generator.gaussian_noise(bg_h, bg_w)
        # elif background_type == 1:  # 单一颜色
        #     background_img = background_generator.plain_color(bg_h, bg_w, bgcolor)
        # elif background_type == 2:  # 准晶背景
        #     background_img = background_generator.quasicrystal(bg_h, bg_w)
        # else:  # 随机图片背景
        background_img = background_generator.picture(bg_h, bg_w)

        # （可选）在此处保存调试： 
        background_img.save("debug_bg.png")

        # ----3. 随机贴文字图到背景----
        tw, th = text_img.width, text_img.height
        bg_width, bg_height = background_img.width, background_img.height

        # 计算可行区域（防止越界）
        max_x = bg_width - margin_right - tw
        max_y = bg_height - margin_bottom - th

        # 计算随机 x
        if max_x < margin_left:
            rand_x = margin_left
        else:
            rand_x = rnd.randint(margin_left, max_x)

        # 计算随机 y
        if max_y < margin_top:
            rand_y = margin_top
        else:
            rand_y = rnd.randint(margin_top, max_y)

        # 贴文字图(若 text_img 带 alpha 通道，可用第三参作为 mask)
        background_img.paste(text_img, (rand_x, rand_y), text_img)
        
        # （可选）在此处保存调试： 
        background_img.save("debug_after_paste.png")

        # ----4. 对整张图做数据增强（旋转、扭曲、缩放、模糊）----
        
        # 4.1 旋转
        if random_skew:
            angle = rnd.randint(-skewing_angle, skewing_angle)
        else:
            angle = skewing_angle
        aug_img = background_img.rotate(angle, expand=True)
        
        # （可选） 
        aug_img.save("debug_after_rotate.png")

        # 4.2 扭曲
        if distortion_type == 1:
            aug_img = distortion_generator.sin(
                aug_img,
                vertical=(distortion_orientation in [0, 2]),
                horizontal=(distortion_orientation in [1, 2])
            )
        elif distortion_type == 2:
            aug_img = distortion_generator.cos(
                aug_img,
                vertical=(distortion_orientation in [0, 2]),
                horizontal=(distortion_orientation in [1, 2])
            )
        elif distortion_type == 3:
            aug_img = distortion_generator.random(
                aug_img,
                vertical=(distortion_orientation in [0, 2]),
                horizontal=(distortion_orientation in [1, 2])
            )
        # （可选） 
        aug_img.save("debug_after_distort.png")

        # 4.3 若指定 height > 0，就按 height 等比缩放，否则按 size
        final_img = aug_img
        final_h = height if height > 0 else size
        if final_h > 0 and final_img.height != final_h:
            ratio = final_h / final_img.height
            new_w = max(1, int(final_img.width * ratio))
            # Pillow>=10 不支持ANTIALIAS，用 LANCZOS 或 Image.Resampling.LANCZOS
            final_img = final_img.resize((new_w, final_h), Image.LANCZOS)
        
        # 4.4 若指定 width>0，对宽度做填充或裁剪
        if width > 0:
            if final_img.width < width:
                # 右侧填充
                padded_img = Image.new("RGB", (width, final_img.height), (255, 255, 255))
                padded_img.paste(final_img, (0, 0))
                final_img = padded_img
            elif final_img.width > width:
                final_img = final_img.crop((0, 0, width, final_img.height))

        # 4.5 模糊
        if blur > 0:
            final_img = final_img.filter(ImageFilter.GaussianBlur(radius=blur))

        # （可选） final_img.save("debug_final.png")

        # ----5. 保存图像----
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        image_name = f"{str(index).zfill(6)}.{extension}"
        save_path = out_dir / image_name
        final_img.convert("RGB").save(save_path)

        # ----6. 写 label.txt----
        parent_dir = out_dir.parent
        label_file = parent_dir / "label.txt"
        with open(label_file, "a", encoding="utf-8") as f:
            rel_path = save_path.relative_to(parent_dir)
            f.write(f"{str(rel_path)}\t{text}\n")

        # ----7. 返回 (可选)----
        return final_img, text