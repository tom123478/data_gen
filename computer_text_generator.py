import random as rnd  # 引入随机模块，用于生成随机数。
import numpy as np  # 引入NumPy模块，尽管这里代码中没有用到它。
from PIL import Image, ImageColor, ImageFont, ImageDraw, ImageFilter  # 从Pillow库导入图像处理相关模块。

# 主函数，用于生成文字图像及其字符边界框。
def generate(text, font_list, text_color, font_size, orientation, space_width, fit, strokewidth, strokefill, cursive):
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


def _generate_horizontal_text(text, font_list, text_color, font_size, space_width, fit, cursive):
    # 随机选择一个主字体
    main_font_path = rnd.choice(font_list)
    main_font = ImageFont.truetype(font=main_font_path, size=font_size)
    
    # 初始化备用字体列表（不包括主字体）
    backup_fonts = [ImageFont.truetype(font=f, size=font_size) for f in font_list if f != main_font_path]
    
    # 初始化变量
    words = text.split(' ')
    space_width = main_font.getsize(' ')[0] * space_width  # 假设空格宽度一致
    char_bbox = []
    ac = 0  # 累计器记录文字位置
    text_width, text_height = 0, 0

    # 遍历单词和字符
    for word in words: # 遍历单词
        for char in word: # 遍历单词中的字符
            char_rendered = False
            try:
                # 尝试用主字体渲染字符
                w, h = main_font.getsize(char) # 获取字符的宽度和高度
                bbox = [[ac, 0], [ac+w, 0], [ac+w, h], [ac, h]] # 定义字符的边界框
                char_bbox.append(bbox) # 将边界框添加到列表中
                text_width = max(text_width, ac + w) # 更新文本宽度
                text_height = max(text_height, h) # 更新文本高度
                ac += w # 更新累计器为下一个字符的位置
                char_rendered = True # 标记字符已渲染
            except Exception:
                # 主字体不支持，尝试备用字体
                for font in backup_fonts:
                    try:
                        w, h = font.getsize(char)
                        bbox = [[ac, 0], [ac+w, 0], [ac+w, h], [ac, h]]
                        char_bbox.append(bbox)
                        text_width = max(text_width, ac + w)
                        text_height = max(text_height, h)
                        ac += w
                        char_rendered = True
                        break  # 成功渲染后退出循环
                    except Exception:
                        continue  # 当前字体失败，尝试下一个字体
            
            if not char_rendered:
                raise ValueError(f"所有字体都不支持字符: {char}")
        
        # 添加单词间的空格宽度
        ac += int(space_width)

    # 创建图像
    txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)

    # 遍历字符边界框并绘制
    for bbox, char in zip(char_bbox, text):
        txt_draw.text((bbox[0][0], bbox[0][1]), char, fill=text_color, font=main_font)

    if fit:
        return txt_img.crop(txt_img.getbbox()), char_bbox
    else:
        return txt_img, char_bbox

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
        txt_draw.text((sum(words_width[0:i]) + i * int(space_width)+gap, gap*2), w, fill=text_color, font=image_font, stroke_width=strokewidth, stroke_fill=strokefill)

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