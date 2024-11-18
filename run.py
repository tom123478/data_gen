import argparse
import os
import sys
import random as rnd
import yaml
from easydict import EasyDict as edict
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool

from string_generator import (
    create_strings_from_dict,
    create_strings_from_file,
    create_strings_randomly
)
from data_generator import FakeTextDataGenerator


def parse_margins(margin_str):
    """
    解析边距参数，将逗号分隔的字符串转换为整数列表。

    参数:
        margin_str (str): 表示边距的字符串，例如 "5,5,5,5" 或 "5"

    返回:
        list: 包含四个整数的列表，分别表示上、右、下、左边距。
    """
    margins = margin_str.split(',')
    if len(margins) == 1:
        return [int(margins[0])] * 4  # 四个边距相同
    return [int(margin) for margin in margins]


def parse_args():
    """
    解析命令行参数和配置文件，返回包含所有参数的命名空间对象。

    返回:
        argparse.Namespace: 包含所有配置参数的对象。
    """
    parser = argparse.ArgumentParser(description="生成合成文本数据")
    parser.add_argument('--cfg', help='配置文件路径', required=False, type=str, default='configs/config.yaml')
    args = parser.parse_args()

    # 加载配置文件
    with open(args.cfg, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)

    # 将配置文件中的参数更新到args对象
    for section in config:
        for key in config[section]:
            setattr(args, key.lower(), config[section][key])

    # 设置默认值
    default_values = {
        'font': None,
        'min_char': 1,
        'max_char': 10,
        'margins': '5,5,5,5',
        'fit': False,
        'bbox': False,
        'label_only': False,
        'thread_count': 1,
        'random_skew': False,
        'random_blur': False,
        'blur': 0,
        'distortion': 0,
        'distortion_orientation': 0,
        'handwritten': False,
        'orientation': 0,
        'space_width': 1.0
    }
    for key, value in default_values.items():
        if not hasattr(args, key):
            setattr(args, key, value)

    return args


def read_color_combinations(file_path):
    """
    从文件中读取前景色和背景色的组合。

    参数:
        file_path (str): 颜色组合文件的路径。

    返回:
        tuple: 两个列表，分别包含前景色和背景色。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [' '.join(line.strip().split()) for line in f]

    font_colors = []
    background_colors = []
    for line in lines:
        color_pair = line.split()
        font_colors.append(color_pair[0])
        background_colors.append(color_pair[1])

    return font_colors, background_colors


def load_fonts(language):
    """
    加载指定语言的字体列表。

    参数:
        language (str): 语言代码，例如 "en"、"ko"。

    返回:
        list: 字体文件路径的列表。
    """
    font_dir = Path('/Users/weicongcong/Desktop/code/data_gen/ocrdata/fonts') / language
    font_paths = [str(font) for font in font_dir.glob('*')]
    for index, font_path in enumerate(font_paths):
        print(f"{index} {font_path}")
    return font_paths


def load_dictionary():
    """
    加载字典文件，获取单词列表。

    返回:
        list: 单词列表。
    """
    dict_file_path = '/Users/weicongcong/Desktop/code/data_gen/ocrdata/texts/Company-Shorter-Form1000.txt'
    with open(dict_file_path, 'r', encoding="utf-8", errors='ignore') as file:
        words_list = [line.strip() for line in file if line.strip()]
    return words_list


def generate_image_paths(args, total_count, train_indices):
    """
    生成图像保存路径和标签文件。

    参数:
        args (argparse.Namespace): 包含配置参数的对象。
        total_count (int): 要生成的图像总数。
        train_indices (list): 标记每个样本是训练集还是验证集的列表。

    返回:
        tuple: 包含训练集和验证集标签文件的路径。
    """
    out_folders = ['train2', 'val2']
    num_digits = 6  # 文件名中的编号位数
    max_files_per_folder = 10000  # 每个文件夹的最大文件数

    # 创建输出目录
    for folder in out_folders:
        Path(args.output_dir, folder).mkdir(parents=True, exist_ok=True)

    num_folders = total_count // max_files_per_folder
    for i in range(num_folders + 1):
        for folder in out_folders:
            Path(args.output_dir, folder, str(i)).mkdir(exist_ok=True)

    # 创建标签文件
    train_label_path = Path(args.output_dir, f"{out_folders[0]}.txt")
    val_label_path = Path(args.output_dir, f"{out_folders[1]}.txt")

    with train_label_path.open('w', encoding="utf8") as train_file, \
            val_label_path.open('w', encoding="utf8") as val_file:
        for i in range(total_count):
            folder_index = i // max_files_per_folder
            filename = f"{str(i).zfill(num_digits)}.{args.extension}"
            image_path = f"{out_folders[train_indices[i]]}/{folder_index}/{filename}"
            label = args.strings[i]
            if train_indices[i] == 0:
                train_file.write(f"{image_path}\t{label}\n")
            else:
                val_file.write(f"{image_path}\t{label}\n")

    return train_label_path, val_label_path


def main():
    """
    主函数，生成合成文本图像数据。
    """
    args = parse_args()  # 解析参数

    # 加载字典和字体
    words_list = load_dictionary()
    if args.font:
        if Path(args.font).exists():
            font_paths = [args.font]
        else:
            sys.exit("无法打开指定的字体文件")
    else:
        font_paths = load_fonts(args.language)

    # 计算要生成的图像总数
    num_words = len(words_list)
    num_fonts = len(font_paths)
    args.count = num_words * num_fonts
    print(f"输出目录: {args.output_dir}")
    print(f"词典单词数: {num_words}")
    print(f"字体数量: {num_fonts}")
    print(f"总图像数: {args.count}")

    # 随机划分训练集和验证集
    num_test = args.count // 10
    num_train = args.count - num_test
    train_indices = [0] * num_train + [1] * num_test  # 0表示训练集，1表示验证集
    rnd.shuffle(train_indices)

    # 生成文本字符串
    if args.input_file:
        print(f"使用指定文件: {args.input_file}")
        args.strings = create_strings_from_file(args.input_file, args.count, args.min_char, args.max_char)
    elif args.random_sequences:
        print("使用随机序列")
        args.strings = create_strings_randomly(
            args.length, args.random, args.count,
            args.include_letters, args.include_numbers, args.include_symbols, args.language
        )
        if args.include_symbols or not any([args.include_letters, args.include_numbers, args.include_symbols]):
            args.name_format = 2  # 适配特殊字符的文件名格式
    else:
        print("使用字典中的字符串")
        args.strings = create_strings_from_dict(args.length, args.random, args.count, words_list)

    total_count = len(args.strings)
    print(f"字符串总数: {total_count}")

    # 设置图像生成参数
    skew_angles = []
    distortions = []
    for text in args.strings:
        length = len(text)
        if length < 5:
            skew_angles.append(7)
            distortions.append(1)
        elif length < 10:
            skew_angles.append(3)
            distortions.append(1)
        else:
            skew_angles.append(0)
            distortions.append(0)

    cursive_flags = [0] * total_count
    for i in range(5 * num_words, 7 * num_words):
        cursive_flags[i] = 15

    # 读取颜色组合
    color_file_path = "/home/jw/data/ocrdata/color_gray.txt"
    font_colors, background_colors = read_color_combinations(color_file_path)
    num_colors = len(font_colors)
    background_types = [1] * num_colors
    background_types[0] = 0
    background_types[1] = 0

    # 生成图像路径和标签文件
    train_label_path, val_label_path = generate_image_paths(args, total_count, train_indices)

    # 准备生成图像的参数列表
    image_params = list(zip(
        range(total_count), # 序号  
        args.strings, # 语料
        [font_paths[i // num_words] for i in range(total_count)], # 字体
        [str(Path(args.output_dir, 'train2' if train_indices[i] == 0 else 'val2', str(i // 10000))) for i in range(total_count)], # 输出路径
        cursive_flags, # 是否斜体
        [args.format] * total_count, # 图像格式
        [args.extension] * total_count, # 图像扩展名
        skew_angles,
        [args.random_skew] * total_count, # 是否随机倾斜
        [args.blur] * total_count, # 是否模糊
        [args.random_blur] * total_count, # 是否随机模糊
        [background_types[i % num_colors] for i in range(total_count)], # 背景类型
        [args.distortion] * total_count, # 是否扭曲
        [args.distortion_orientation] * total_count, # 扭曲方向
        [args.handwritten] * total_count, # 是否手写
        [args.name_format] * total_count, # 名称格式
        [args.width] * total_count, # 宽度
        [args.alignment] * total_count, # 对齐方式
        [font_colors[i % num_colors] for i in range(total_count)], # 前景色
        [args.orientation] * total_count, # 图像方向
        [args.space_width] * total_count, # 空格宽度
        [parse_margins(args.margins)] * total_count, # 边距
        [args.fit] * total_count, # 是否适应
        [args.bbox] * total_count, # 是否bbox
        [args.label_only] * total_count, # 是否仅标签
        [background_colors[i % num_colors] for i in range(total_count)], # 背景色
        [0] * total_count,  # 描边宽度
        [''] * total_count  # 描边颜色
    ))

    # 使用多进程生成图像
    with Pool(args.thread_count) as pool:
        list(tqdm(pool.imap_unordered(FakeTextDataGenerator.generate_from_tuple, image_params), total=total_count))

    print("数据生成完成！")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("程序被用户中断")
        sys.exit(0)
