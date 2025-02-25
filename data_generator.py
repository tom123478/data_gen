import random as rnd
import numpy as np
from pathlib import Path

import computer_text_generator
import background_generator

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
        width,                 # 期望的最终图像宽度（<=0则自适应文字宽）
        text_color,
        orientation,
        space_width,
        margins,               # "top,left,bottom,right"
        fit,
        stroke_width,
        stroke_fill,
        height=0               # 若>0，则最终图像高度 = height
    ):
        """
        1) 生成文字图 (text_img)
        2) 旋转 text_img
        3) 创建背景并将旋转后的文字图贴在背景上
        4) 其它数据增强处理
        5) 保存并写 label
        """

        # ----0. 解析边距----
        margin_top, margin_left, margin_bottom, margin_right = map(int, margins.split(','))
        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        # ----1. 生成文字图 (整行)----
        #    computer_text_generator.generate 返回 (text_img, box_info)
        text_img, _ = computer_text_generator.generate(
            out_dir,
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

        # ----2. 旋转文字图----

        # 这里演示：根据字符串长度，简单地设定不同 skew_angle & distortion
        width_text, _ = text_img.size
        if width_text>250:
            angle = rnd.randint(-0.1*skewing_angle, 0.1*skewing_angle)
        elif width_text>200:
            angle = rnd.randint(-0.3*skewing_angle, 0.3*skewing_angle)
        elif width_text>150:
            angle = rnd.randint(-0.5*skewing_angle, 0.5*skewing_angle)
        elif width_text>100:
            angle = rnd.randint(-0.7*skewing_angle, 0.7*skewing_angle)
        else:
            angle = rnd.randint(-skewing_angle, skewing_angle)
        
        # expand=True 可以让旋转后的图像包含完整内容
        rotated_text_img = text_img.rotate(angle, expand=True)

        # 获取旋转后文字图的尺寸
        rtw, rth = rotated_text_img.size

        # （调试）可视化
        # rotated_text_img.save("debug_rotated_text_img.png")

        # ----3. 创建背景图并把旋转文字贴上去----
        #   这里背景最小高度是 size, 如果旋转后比 size 更高，就取 rth
        bg_h = rth + vertical_margin
        bg_w = rtw + horizontal_margin

        # 如果你有多种背景模式，这里按需要调用不同生成函数，这里只是示例
        background_img = background_generator.picture(bg_h, bg_w)

        # 计算可以贴的最大 x / y 范围，防止越界
        max_x = bg_w - margin_right - rtw
        max_y = bg_h - margin_bottom - rth

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

        # 把旋转后的文字图贴到背景图 (使用自身作为 mask 以保留透明度)
        background_img.paste(rotated_text_img, (rand_x, rand_y), rotated_text_img)

        # （调试）查看效果
        # background_img.save("debug_after_paste.png")

        # ----4. 接下来做其它扭曲 / 缩放 / blur 等数据增强操作----
        final_img = background_img

        # ----5. 保存图像----
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        image_name = f"{str(index).zfill(8)}.{extension}"
        save_path = out_dir / image_name
        final_img.save(save_path, quality=95)

        # ----6. 写 label.txt----
        parent_dir = out_dir.parent
        label_file = parent_dir / "label.txt"
        with open(label_file, "a", encoding="utf-8") as f:
            rel_path = save_path.relative_to(parent_dir)
            f.write(f"{str(rel_path)}\t{text}\n")