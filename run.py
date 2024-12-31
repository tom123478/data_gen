import argparse
import sys
import yaml
from easydict import EasyDict as edict
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
import time

from string_generator import (
    create_strings_from_dict,
    create_strings_from_corpus_file,
    create_strings_randomly_from_chars
)
from data_generator import FakeTextDataGenerator


def parse_margins(margin_str):
    """
    边距就是字符离左右上下边界的距离
    将逗号分隔的字符串转换为整数列表，用于设置边距。
    示例:
        "5" -> [5, 5, 5, 5]
        "5,10,5,10" -> [5, 10, 5, 10]
    """
    margins = margin_str.split(',')
    if len(margins) == 1:
        # 如果只给定一个值，则四个边距相同
        return [int(margins[0])] * 4
    return [int(m) for m in margins]


def parse_args():
    """
    解析命令行参数和配置文件，返回包含所有参数的命名空间对象。
    """
    parser = argparse.ArgumentParser(description="Generate Synthetic Text Data")
    parser.add_argument('--cfg',
                        help='Path of config file',
                        required=False,
                        type=str,
                        default='configs/config.yaml')
    args = parser.parse_args()

    # 加载配置文件
    try:
        with open(args.cfg, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        config = edict(config)
    except Exception as e:
        sys.exit(f"[Error] Failed to load YAML config: {e}")

    # 将配置文件中的参数更新到args对象
    # 假定配置文件的结构类似:
    #   SECTION:
    #     key: value
    for section in config:
        for key in config[section]:
            setattr(args, f"{key.lower()}", config[section][key])
    return args

def load_fonts(font_or_dir):
    """
    加载指定路径（文件或目录）下的字体列表。
    如果 font_or_dir 是文件，则只返回该文件。
    如果是目录，则返回目录下所有文件。
    """
    p = Path("/Users/weicongcong/Desktop/code/data_gen/ocrdata/fonts/"+font_or_dir)
    if not p.exists():
        sys.exit(f"[Error] Font path does not exist: {font_or_dir}")

    if p.is_file():
        # 传入的是一个具体字体文件路径
        return [str(p)]
    else:
        # 从某个目录加载所有字体
        font_paths = [str(font) for font in p.glob('*') if font.is_file()]
        if not font_paths:
            sys.exit(f"[Error] No font files found in directory: {font_or_dir}")
        return font_paths


def load_corpus(corpus_file_path):
    """
    加载语料库文件，返回行列表。
    """
    p = Path(corpus_file_path)
    if not p.exists():
        sys.exit(f"[Error] Corpus file not found: {corpus_file_path}")
    with open(p, 'r', encoding="utf-8-sig", errors='ignore') as file:
        words_list = [line.strip() for line in file if line.strip()]
    return words_list

def worker(param_tuple):
    """
    包装函数，给多进程调用用的。
    """
    return FakeTextDataGenerator.generate(*param_tuple)

def main():
    # 1. 解析参数
    args = parse_args()

    # 2. 加载语料库
    corpus_list = load_corpus(args.corpus)
    num_texts = len(corpus_list)
    print(f"Loaded corpus with {num_texts} lines")

    # 3. 加载字体
    if args.fonts:
        font_paths = load_fonts(args.fonts)
    else:
        font_paths = load_fonts('ch')  # 默认从 'ch' 目录加载
    num_fonts = len(font_paths)
    print(f"Loaded {num_fonts} fonts")

    # 4. 根据 corpus_type 生成字符串列表
    if args.corpus_type.upper() == "CORPUS":
        print(f"Use corpus file: {args.corpus}")
        args.strings = create_strings_from_corpus_file(args.corpus)
    elif args.corpus_type.upper() == "RANDOM":
        print("Use random sequences from chars")
        args.strings = create_strings_randomly_from_chars(
            length=args.length,
            allow_variable=args.random,
            count=args.count,
            include_letters=args.include_letters,
            include_numbers=args.include_numbers,
            include_symbols=args.include_symbols,
            language=args.language
        )
        # 如果包含符号，或者其他条件不符合，就强制 name_format=2
        if args.include_symbols or not any([
            args.include_letters,
            args.include_numbers,
            args.include_symbols
        ]):
            args.name_format = 2
    else:
        print("Use strings from dict")
        args.strings = create_strings_from_dict(
            args.length,
            args.random,
            args.count,
            corpus_list
        )

    total_count = len(args.strings)
    print(f"Total strings: {total_count}")

    # 5. 设置颜色
    font_color = tuple(map(int, args.color.strip("()").split(",")))
    font_colors = [font_color]
    num_colors = len(font_colors)

    # 6. 构造参数列表
    cursive_flags = [0] * total_count
    margins_str = args.margins
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_params = []
    for i in range(total_count):
        color_idx = i % num_colors
        param_tuple = (
            i,
            args.strings[i],
            font_paths,
            str(output_dir),
            cursive_flags[i],
            args.size,
            args.extension,
            args.skew_angle,
            args.distortion,
            args.distortion_orientation,
            args.width,
            font_colors[color_idx],
            args.orientation,
            args.space_width,
            margins_str,
            args.fit,
            args.stroke_width,
            args.stroke_fill,
            args.height
        )
        image_params.append(param_tuple)

    print("开始生成图像...")
    start_time = time.time()

    # 7. 多进程 / 单进程
    if args.num_workers <= 1:
        # 单进程执行
        for params in tqdm(image_params, total=total_count):
            FakeTextDataGenerator.generate(*params)
    else:
        # 多进程执行
        with Pool(processes=args.num_workers) as pool:
            for _ in tqdm(pool.imap_unordered(worker, image_params), total=total_count):
                pass

    end_time = time.time()
    print("数据生成完成！")
    print(f"运行时间: {end_time - start_time} 秒")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"[Error] {e}")
        sys.exit(1)