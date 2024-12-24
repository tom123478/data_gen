import argparse
import os
import sys
import random as rnd
import yaml
from easydict import EasyDict as edict
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
import re

from string_generator import (
    create_strings_from_dict,
    create_strings_from_corpus_file,
    create_strings_randomly_from_chars
)
from data_generator import FakeTextDataGenerator


def parse_margins(margin_str):
    """
    解析边距参数，将逗号分隔的字符串转换为整数列表。
    例如 "5,5,5,5" 或 "5"。
    """
    margins = margin_str.split(',')
    if len(margins) == 1:
        return [int(margins[0])] * 4  # 四个边距相同
    return [int(margin) for margin in margins]


def parse_args():
    """
    解析命令行参数和配置文件，返回包含所有参数的命名空间对象。
    """
    parser = argparse.ArgumentParser(description="generate synthetic text data")
    parser.add_argument('--cfg', help='path of config file', required=False, type=str, default='configs/config.yaml')
    args = parser.parse_args()

    # 加载配置文件
    with open(args.cfg, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)

    # 将配置文件中的参数更新到args对象
    for section in config:
        for key in config[section]:
            setattr(args, f"{key.lower()}", config[section][key])
    return args


def read_color_combinations(file_path):
    """
    从文件中读取前景色和背景色的组合。文件格式示例:
        (255,0,0) (0,0,0)
        (128,128,128) (255,255,255)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    font_colors = []
    background_colors = []

    for line in lines:
        parts = line.split()
        # 解析前景色
        font_color = tuple(map(int, parts[0].strip("()").split(",")))
        # 解析背景色
        background_color = tuple(map(int, parts[1].strip("()").split(",")))
        font_colors.append(font_color)
        background_colors.append(background_color)

    return font_colors, background_colors


def load_fonts(fonts):
    """
    加载指定语言/目录的字体列表。
    """
    font_dir = Path('/Users/weicongcong/Desktop/code/data_gen/ocrdata/fonts') / fonts
    font_paths = [str(font) for font in font_dir.glob('*') if font.is_file()]
    for index, font_path in enumerate(font_paths):
        print(f"{index} {font_path}")
    return font_paths


def load_corpus(corpus_file_path):
    """
    加载语料库文件，返回行列表。
    """
    with open(corpus_file_path, 'r', encoding="utf-8-sig", errors='ignore') as file:
        words_list = [line.strip() for line in file if line.strip()]
    return words_list


def main():
    args = parse_args()  # 解析参数

    # 加载语料库
    corpus_list = load_corpus(args.corpus)
    print(f"corpus words nums: {len(corpus_list)}")

    # 加载字体
    if args.fonts:
        if Path(args.fonts).exists():
            # 传入的是一个单字体文件路径
            font_paths = [args.fonts]
        else:
            sys.exit("无法打开指定的字体文件")
    else:
        # 从某个目录加载所有字体
        font_paths = load_fonts('ch')

    num_texts = len(corpus_list)
    num_fonts = len(font_paths)

    print(f"output dir: {args.output_dir}")
    print(f"corpus nums: {num_texts}")
    print(f"font nums: {num_fonts}")

    # 根据 corpus_type 生成字符串列表
    if args.corpus_type == "CORPUS":
        print(f"use corpus file: {args.corpus}")
        args.strings = create_strings_from_corpus_file(args.corpus)
    elif args.corpus_type == "RANDOM":
        print("use random sequences from chars")
        args.strings = create_strings_randomly_from_chars(
            length=args.length,
            allow_variable=args.random,
            count=args.count,
            include_letters=args.include_letters,
            include_numbers=args.include_numbers,
            include_symbols=args.include_symbols,
            language=args.language
        )
        # 如果包含符号，或者其他条件不符合，就做 name_format=2
        if args.include_symbols or not any([args.include_letters, args.include_numbers, args.include_symbols]):
            args.name_format = 2
    else:
        print("use strings from dict")
        args.strings = create_strings_from_dict(args.length, args.random, args.count, corpus_list)

    total_count = len(args.strings)
    print(f"total strings: {total_count}")

    # cursive_flags 这里写死全为0，也可自行设置不同策略
    cursive_flags = [0] * total_count

    # 读取前景色 & 背景色组合
    color_file_path = "/Users/weicongcong/Desktop/code/data_gen/ocrdata/color/color.txt"
    font_colors, background_colors = read_color_combinations(color_file_path)
    num_colors = len(font_colors)

    # 创建输出目录/标签文件
    # label_path = generate_image_paths(args)

    margins_str = args.margins

    image_params = []
    for i in range(total_count):
        # 选一个颜色组合
        color_idx = i % num_colors
        # 将一整套参数打包成 tuple
        param_tuple = (
            i,                             # index
            args.strings[i],              # text
            font_paths,                   # font_list
            str(Path(args.output_dir)),   # out_dir
            cursive_flags[i],             # cursive
            args.size,                    # size
            args.extension,               # extension
            args.skew_angle,               # skewing_angle
            args.distortion,               # distortion_type
            args.distortion_orientation,  # distortion_orientation
            args.width,                   # width
            font_colors[color_idx],       # text_color
            args.orientation,             # orientation
            args.space_width,             # space_width
            margins_str,                  # margins
            args.fit,                     # fit
            args.stroke_width,            # strokewidth
            args.stroke_fill,             # strokefill
            args.height                   # height
        )
        image_params.append(param_tuple)

    print("开始生成图像...")

    # 方式1: 单进程
    for params in tqdm(image_params, total=total_count):
        FakeTextDataGenerator.generate(*params)

    # # 方式2: 多进程 (如果你想使用CPU多核加速)
    # num_workers = getattr(args, 'num_workers', 1)  # 从args里读取或默认1
    # with Pool(processes=num_workers) as p:
    #     # imap_unordered 按任意完成顺序返回结果
    #     for _ in tqdm(p.imap_unordered(FakeTextDataGenerator.generate, image_params), total=total_count):
    #         pass

    print("数据生成完成！")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("程序被用户中断")
        sys.exit(0)