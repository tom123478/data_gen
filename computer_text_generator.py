import random as rnd  # 引入随机模块，用于生成随机数。
import numpy as np  # 引入NumPy模块，尽管这里代码中没有用到它。
from PIL import Image, ImageColor, ImageFont, ImageDraw, ImageFilter  # 从Pillow库导入图像处理相关模块。

# 主函数，用于生成文字图像及其字符边界框。
def generate(text, font_list, text_color, font_size, orientation, space_width, 
             fit, strokewidth, strokefill, cursive):
    if orientation == 0:  # 如果文字方向是水平的。
        # 如果设置了描边宽度，调用带描边的水平文字生成函数。
        if strokewidth > 0:
            return _generate_horizontal_text_stroke(text, font_list, text_color, font_size, space_width, fit, strokewidth, strokefill)
        else:  # 否则调用普通的水平文字生成函数。
            return _generate_horizontal_text(text, font_list, text_color, font_size, space_width, fit, cursive)
    elif orientation == 1:  # 如果文字方向是垂直的。
        return _generate_vertical_text(text, font_list, text_color, font_size, space_width, fit)
    else:  # 如果输入了未知方向，抛出异常。
        raise ValueError("Unknown orientation " + str(orientation))

def _generate_horizontal_text(
    text,
    font_list,
    text_color=(0, 0, 0),
    font_size=32,
    space_width=1.0,
    fit=True,
    cursive=False
):
    """
    根据给定文本和字体列表，生成一行水平排布的文字图像。
    如果某个字符在所有字体都不支持，则返回 (空图, [])。
    
    参数:
        text        : 需要绘制的字符串
        font_list   : 可选字体路径列表 (list of str)
        text_color  : (R, G, B) 文字颜色
        font_size   : 字号大小
        space_width : 空格宽度相对于常规空格的倍数
        fit         : 是否在最后对图像进行 crop 来去掉透明边缘
        cursive     : 示例里未使用，可自行扩展

    返回:
        (PIL.Image, [list of char_bbox])，其中 char_bbox 是每个字符在图像中的四点坐标。
    """
    import random as rnd
    from PIL import Image, ImageFont, ImageDraw

    # 便于后面统一使用的函数 get_char_bbox -> (left, top, right, bottom)
    def get_char_bbox(font, ch):
        return font.getbbox(ch)

    # 1. 随机选择一个主字体
    main_font_path = rnd.choice(font_list)
    main_font = ImageFont.truetype(font=main_font_path, size=font_size)

    # 2. 初始化备用字体列表
    backup_fonts = [
        ImageFont.truetype(font=f, size=font_size)
        for f in font_list
        if f != main_font_path
    ]

    # 3. 计算空格宽度 (以主字体为准，也可改成单独测量空格)
    space_left, space_top, space_right, space_bottom = main_font.getbbox(' ')
    single_space_width = space_right - space_left
    space_width_pixels = int(single_space_width * space_width)

    # ---------- 第一阶段：测量每个字符的 bbox ----------
    char_bboxes = []
    rendered_fonts = []

    for char in text:
        bbox = None
        chosen_font = None

        # 先尝试主字体
        try:
            l, t, r, b = get_char_bbox(main_font, char)
            if (r - l) > 0 and (b - t) > 0:
                bbox = (l, t, r, b)
                chosen_font = main_font
            else:
                raise Exception("Main font fails.")
        except:
            # 如果主字体不支持，就尝试备用字体
            for bf in backup_fonts:
                try:
                    l, t, r, b = get_char_bbox(bf, char)
                    if (r - l) > 0 and (b - t) > 0:
                        bbox = (l, t, r, b)
                        chosen_font = bf
                        break
                except:
                    continue

        if bbox is None:
            # 所有字体都不支持该字符，返回空图和空列表
            empty_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
            return empty_img, []

        char_bboxes.append(bbox)
        rendered_fonts.append(chosen_font)

    # ---------- 第二阶段：计算整行最合理的宽高 ----------
    total_width = 0
    min_top = float('inf')
    max_bottom = float('-inf')

    for (l, t, r, b) in char_bboxes:
        w = (r - l)
        total_width += w
        if t < min_top:
            min_top = t
        if b > max_bottom:
            max_bottom = b

    # 如果要在末尾加空格：
    # total_width += space_width_pixels

    # 整行文字的高度
    line_height = max_bottom - min_top

    # 如果全部字符加起来宽度或高度不合理，则返回空图
    if total_width <= 0 or line_height <= 0:
        empty_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        return empty_img, []

    # ---------- 第三阶段：创建画布并绘制 ----------
    txt_img = Image.new('RGBA', (total_width, line_height), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)

    current_x = 0
    char_bbox_list = []

    for i, char in enumerate(text):
        (l, t, r, b) = char_bboxes[i]
        font = rendered_fonts[i]

        w = (r - l)
        h = (b - t)

        # 【关键改动】令整行最上方 y=0 对应 min_top
        # 只需统一用 y_draw = -min_top，即把“最上字符的 top”顶到 0 的位置
        x_draw = current_x - l
        y_draw = -min_top

        # 绘制字符
        txt_draw.text((x_draw, y_draw), char, fill=text_color, font=font)

        # 记录该字符在最终图像中的四点坐标
        # 左上: (x_draw + l, y_draw + t) = (current_x, y_draw + t + l - l) => 还是别绕晕
        # 这里为了返回给用户一个「字符外框」，我们按照“最终像素坐标”来：
        left_px = x_draw + l
        top_px  = y_draw + t
        right_px = x_draw + r
        bottom_px = y_draw + b
        char_bbox = [
            [left_px,  top_px   ],
            [right_px, top_px   ],
            [right_px, bottom_px],
            [left_px,  bottom_px]
        ]
        char_bbox_list.append(char_bbox)

        current_x += w

    # ---------- 第四阶段：如果 fit=True，就裁剪空白 ----------
    #   getbbox() 返回整个画布真正有内容的区域 (left, top, right, bottom)
    if fit and txt_img.getbbox() is not None:
        cropped_img = txt_img.crop(txt_img.getbbox())
        crop_left, crop_upper, _, _ = txt_img.getbbox()

        # 裁剪之后，还要把 bbox 也往左上移动
        for bbox in char_bbox_list:
            for pt in bbox:
                pt[0] -= crop_left
                pt[1] -= crop_upper

        return cropped_img, char_bbox_list
    else:
        return txt_img, char_bbox_list

# 普通水平文字生成函数。
def _generate_horizontal_text_orign(text, font, text_color, font_size, space_width, fit, cursive):
    image_font = ImageFont.truetype(font=font, size=font_size)  # 加载指定字体及字体大小。
    words = text.split(' ')  # 将输入文本按空格分割为单词列表。
    space_width = image_font.getsize(' ')[0] * space_width  # 计算空格的宽度，根据比例调整。

    words_width = [image_font.getsize(w)[0] for w in words]  # 计算每个单词的宽度。
    text_width = sum(words_width) + int(space_width) * (len(words) - 1) + cursive  # 计算整行文本的总宽度。
    text_height = max([image_font.getsize(w)[1] for w in words])  # 计算文本的高度。

    char_bbox = []  # 存储每个字符的边界框信息。
    ac = 0  # 累计器，用于跟踪字符的横坐标。

    # 遍历每个单词和字符，计算边界框。
    for word in words:
        for char in word:
            w, h = image_font.getsize(char)  # 获取字符的宽度和高度。
            bbox = [[ac, 0], [ac+w, 0], [ac+w, h], [ac, h]]  # 定义字符的边界框。
            char_bbox.append(bbox)  # 将边界框添加到列表中。
            ac += image_font.getsize(char)[0]  # 更新累计器为下一个字符的位置。
        ac += int(space_width)  # 添加单词之间的空格宽度。

    # 创建一张透明背景的图片。
    txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))

    # 创建绘图对象。
    txt_draw = ImageDraw.Draw(txt_img)

    # 解析输入的颜色范围。
    colors = [ImageColor.getrgb(c) for c in text_color.split(',')]
    c1, c2 = colors[0], colors[-1]

    # 随机生成填充颜色，颜色在范围 c1 和 c2 之间。
    fill = (
        rnd.randint(min(c1[0], c2[0]), max(c1[0], c2[0])),
        rnd.randint(min(c1[1], c2[1]), max(c1[1], c2[1])),
        rnd.randint(min(c1[2], c2[2]), max(c1[2], c2[2]))
    )

    # 遍历每个单词并绘制到图片上。
    for i, w in enumerate(words):
        txt_draw.text((cursive + sum(words_width[0:i]) + i * int(space_width), 0), w, fill=fill, font=image_font)

    # 如果设置了 `fit`，裁剪掉多余的空白区域。
    if fit:
        return txt_img.crop(txt_img.getbbox()), char_bbox
    else:
        return txt_img, char_bbox

# 带描边的水平文字生成函数。
def _generate_horizontal_text_stroke(text, font, text_color, font_size, space_width, fit, strokewidth, strokefill):
    gap = 6  # 为描边和文本留出的额外间距。
    image_font = ImageFont.truetype(font=font, size=font_size)  # 加载字体。
    words = text.split(' ')  # 分割文本为单词。
    space_width = (image_font.getsize(' ')[0]+gap) * space_width  # 计算带间距的空格宽度。

    words_width = [image_font.getsize(w)[0] for w in words]  # 计算每个单词的宽度
    text_width = sum(words_width) + int(space_width) * (len(words) - 1) + gap*2  # 计算总宽度。
    text_height = max([image_font.getsize(w)[1] for w in words]) + gap*3  # 计算总高度。

    char_bbox = []  # 存储字符的边界框。
    ac = 0  # 累计器。

    # 遍历字符并计算边界框。
    for word in words:
        for char in word:
            w, h = image_font.getsize(char)
            bbox = [[ac, 0], [ac+w, 0], [ac+w, h], [ac, h]]
            char_bbox.append(bbox)
            ac += image_font.getsize(char)[0]
        ac += int(space_width)

    # 创建图片并绘制文字。
    txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    colors = [ImageColor.getrgb(c) for c in text_color.split(',')]
    c1, c2 = colors[0], colors[-1]
    fill = (
        rnd.randint(min(c1[0], c2[0]), max(c1[0], c2[0])),
        rnd.randint(min(c1[1], c2[1]), max(c1[1], c2[1])),
        rnd.randint(min(c1[2], c2[2]), max(c1[2], c2[2]))
    )

    # 绘制文字，添加描边。
    for i, w in enumerate(words):
        txt_draw.text((sum(words_width[0:i]) + i * int(space_width)+gap, gap*2), w, fill=text_color,
                       font=image_font, stroke_width=strokewidth, stroke_fill=strokefill)

    if fit:
        return txt_img.crop(txt_img.getbbox()), char_bbox
    else:
        return txt_img, char_bbox

# 垂直文字生成函数。
def _generate_vertical_text(text, font, text_color, font_size, space_width, fit):
    image_font = ImageFont.truetype(font=font, size=font_size)  # 加载字体。
    space_height = int(image_font.getsize(' ')[1] * space_width)  # 计算空格高度。

    # 计算每个字符的高度。
    char_heights = [image_font.getsize(c)[1] if c != ' ' else space_height for c in text]
    text_width = max([image_font.getsize(c)[0] for c in text])  # 计算文本的最大宽度。
    text_height = sum(char_heights)  # 计算总高度。

    char_bbox = []  # 存储字符边界框。
    ac = 0  # 累计器。

    # 遍历字符并计算边界框。
    words = text.split(' ')
    for word in words:
        for char in word:
            w, h = image_font.getsize(char)
            bbox = [[0, ac], [w, ac], [w, ac+h], [0, ac+h]]
            char_bbox.append(bbox)
            ac += image_font.getsize(char)[1]
        ac += int(space_height)

    # 创建图片并绘制文字。
    txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    colors = [ImageColor.getrgb(c) for c in text_color.split(',')]
    c1, c2 = colors[0], colors[-1]
    fill = (
        rnd.randint(c1[0], c2[0]),
        rnd.randint(c1[1], c2[1]),
        rnd.randint(c1[2], c2[2])
    )

    for i, c in enumerate(text):
        txt_draw.text((0, sum(char_heights[0:i])), c, fill=fill, font=image_font)

    if fit:
        return txt_img.crop(txt_img.getbbox()), char_bbox
    else:
        return txt_img, char_bbox