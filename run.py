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
    create_strings_from_corpus_file,
    create_strings_randomly_from_chars
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
    parser = argparse.ArgumentParser(description="generate synthetic text data")
    parser.add_argument('--cfg', help='path of config file', required=False, type=str, default='configs/config.yaml')
    args = parser.parse_args()

    # 加载配置文件
    with open(args.cfg, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)

    # 将配置文件中的参数更新到args对象
    for section in config:
        for key in config[section]:
            setattr(args, f"{key.lower()}", config[section][key])
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


def load_fonts(fonts):
    """
    加载指定语言的字体列表。

    参数:
        font (str): 字体文件夹名称，例如 "en"、"ko"。

    返回:
        list: 字体文件路径的列表。
    """
    font_dir = Path('/Users/weicongcong/Desktop/code/data_gen/ocrdata/fonts') / fonts
    font_paths = [str(font) for font in font_dir.glob('*')]
    for index, font_path in enumerate(font_paths):
        print(f"{index} {font_path}")
    return font_paths


def load_corpus(corpus_file_path):
    """
    加载字典文件，获取单词列表。

    返回:
        list: 单词列表。
    """
    with open(corpus_file_path, 'r', encoding="utf-8", errors='ignore') as file:
        words_list = [line.strip() for line in file if line.strip()]
    return words_list


def generate_image_paths(args, total_count):
    """
    生成图像保存路径和标签文件。

    参数:
        args (argparse.Namespace): 包含配置参数的对象。
        total_count (int): 要生成的图像总数。

    返回:
        Path: 标签文件的路径。
    """
    num_digits = 6

    # 创建输出目录
    output_dir = Path(args.FILE_SETTINGS.OUTPUT_DIR)
    label_file_path = output_dir / 'label.txt'
    output_images_dir = output_dir / 'images'
    output_images_dir.mkdir(parents=True, exist_ok=True)  # 确保图像目录存在

    # 打开标签文件并写入内容
    with label_file_path.open('w', encoding="utf8") as label_file:
        for i in range(total_count):
            # 生成文件名
            filename = f"{str(i).zfill(num_digits)}.jpg"
            image_path = output_images_dir / filename

            # 获取对应的标签
            if i < len(args.strings):  # 防止索引越界
                label = args.corpus[i]
            else:
                label = "unknown"  # 为多余样本提供默认标签

            # 写入标签文件
            label_file.write(f"{image_path}\t{label}\n")

    return label_file_path

def main():
    """
    主函数，生成合成文本图像数据。
    """
    args = parse_args()  # 解析参数

    # 加载语料库
    corpus_list = load_corpus(args.corpus)
    print(f"corpus words nums: {len(corpus_list)}")

    if args.fonts:
        if Path(args.fonts).exists():
            font_paths = [args.fonts]
        else:
            sys.exit("无法打开指定的字体文件")
    else:
        font_paths = load_fonts('ch')

    # 计算要生成的图像总数
    num_texts = len(corpus_list)
    num_fonts = len(font_paths)

    print(f"output dir: {args.FILE_SETTINGS.OUTPUT_DIR}")
    print(f"corpus nums: {num_texts}")
    print(f"font nums: {num_fonts}")
    print(f"total generate images: {num_texts}")

    # 生成文本字符串
    if args.corpus_type == "CORPUS":
        print(f"use corpus file: {args.corpus}")
        args.strings = create_strings_from_corpus_file(args.corpus)
    elif args.corpus_type == "RANDOM":
        print("use random sequences from chars")
        args.strings = create_strings_randomly_from_chars(
            args.length, args.random, args.count,
            args.include_letters, args.include_numbers, args.include_symbols, args.language
        )
        if args.include_symbols or not any([args.include_letters, args.include_numbers, args.include_symbols]):
            args.name_format = 2
    else:
        print("use strings from dict")
        args.strings = create_strings_from_dict(args.length, args.random, args.count, corpus_list)

    total_count = len(args.strings)
    print(f"total strings: {total_count}")

    # 数据增强-旋转和扭曲
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
    for i in range(5 * num_texts, 7 * num_texts):
        cursive_flags[i] = 15

    # 读取颜色组合
    color_file_path = "/home/jw/data/ocrdata/color_gray.txt"
    font_colors, background_colors = read_color_combinations(color_file_path)
    num_colors = len(font_colors)
    background_types = [1] * num_colors
    background_types[0] = 0
    background_types[1] = 0

    # 生成图像路径和标签文件
    label_path = generate_image_paths(args, total_count)

    # 准备生成图像的参数列表
    image_params = list(zip(
        range(total_count), 
        args.strings, 
        [font_paths] * total_count,
        [str(Path(args.output_dir))] * total_count, 
        cursive_flags,
        [args.format] * total_count, 
        [args.extension] * total_count, 
        skew_angles,
        [args.random_skew] * total_count, 
        [args.blur] * total_count, 
        [args.random_blur] * total_count,
        [background_types[i % num_colors] for i in range(total_count)],
        [args.distortion] * total_count, 
        [args.distortion_orientation] * total_count,
        [args.handwritten] * total_count, 
        [args.name_format] * total_count,
        [args.width] * total_count, 
        [args.alignment] * total_count,
        [font_colors[i % num_colors] for i in range(total_count)],
        [args.orientation] * total_count, 
        [args.space_width] * total_count,
        [parse_margins(args.margins)] * total_count, 
        [args.fit] * total_count,
        [args.bbox] * total_count, 
        [args.label_only] * total_count,
        [background_colors[i % num_colors] for i in range(total_count)], 
        [0] * total_count, [''] * total_count
    ))

    # 单进程生成图像
    print("开始生成图像...")
    for params in tqdm(image_params, total=total_count):  # tqdm 进度条
        FakeTextDataGenerator.generate(params)

    print("数据生成完成！")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("程序被用户中断")
        sys.exit(0)