import argparse
import os, errno
import random as rnd
import re
import sys
import pickle
import yaml
from easydict import EasyDict as edict

from pathlib import Path
from tqdm import tqdm
from string_generator import (
    create_strings_from_dict,
    create_strings_from_file,
    create_strings_randomly
)
from data_generator import FakeTextDataGenerator
from multiprocessing import Pool

def margins(margin):
    # 解析边距参数，将一个逗号分隔的字符串分解成列表
    margins = margin.split(',')
    if len(margins) == 1:
        return [margins[0]] * 4  # 如果只提供一个数字，那么四边使用相同的边距
    return [int(m) for m in margins]  # 将字符串转换为整数列表



def parse_arg1():
    parser = argparse.ArgumentParser(description="gen data")
    parser.add_argument('--cfg',help='gen data config file path',required=True,type=str,default='configs/config.yaml')
    args = parser.parse_args()

    with open(args.cfg,'r') as f:
        config = yaml.load(f,Loader=yaml.FullLoader)
        config = edict(config)


def read_colorcomb(file_i):
    # 读取文件以获取前景色和背景色组合
    with open(file_i, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]        
    f.close()
    
    num_comb = len(lines)
    color_font = []
    color_back = []
    # 从文件中读取每一行，并将前景色和背景色分别存入两个列表
    for l in lines:
        line = l.split()
        color_font.append(line[0])
        color_back.append(line[1])

    return color_font, color_back

def load_fonts(lang):
    # 根据指定的语言加载字体列表
    fontlist = [str(font) for font in (Path('/home/jw/code/ocrdata/fonts') / lang).glob('*')]
    n = 0
    for item in fontlist:
        print(str(n) + " " + item)  # 打印字体索引和路径
        n += 1
    return fontlist

def load_dict(): 
    # 加载指定语言的字典文件
    lang_dict = []    
    dict_file = '/home/jw/data/ocrdata/words ko all.txt' # 指定字典文件
    
    with (Path(dict_file)).open('r', encoding="utf8", errors='ignore') as d:
        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]

    return lang_dict

def main():
    args = parse_arguments()      # 解析命令行参数
        
    ### 如果输出目录不存在，则创建它。
    outfolder = ['train2','val2']    
    try:
        Path(args.output_dir+'/'+outfolder[0]).mkdir(exist_ok=True)
        Path(args.output_dir+'/'+outfolder[1]).mkdir(exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # 创建单词列表
    lang_dict = load_dict()

    # 创建字体列表（路径）
    if not args.font:
        fonts = load_fonts(args.language)
    else:
        if Path(args.font).exists():
            fonts = [args.font]  # 如果指定了单个字体文件，仅使用该文件
        else:
            sys.exit("无法打开字体文件")

    num_digit = 6  # 定义文件名中编号的位数
    num_maxfile = 10000  # 每个文件夹的最大文件数
    wc = len(lang_dict)  # 词典中单词的数量
    fc = len(fonts)  # 可用字体的数量
    args.count = wc * fc  # 总的生成图像数
    print(args.output_dir)
    print('lang_dict: ', str(wc))
    print('fonts: ', str(fc))
    print('count:' + str(args.count))

    nfolders = int(args.count / num_maxfile)  # 需要的文件夹数量
    for i in range(nfolders + 1):
        Path(args.output_dir + '/' + outfolder[0] + '/' + str(i)).mkdir(exist_ok=True)
        Path(args.output_dir + '/' + outfolder[1] + '/' + str(i)).mkdir(exist_ok=True)

    # 设置训练/测试数据比例
    num_test = int(args.count / 10)
    num_train = args.count - num_test
    iFolder = num_train * [0] + num_test * [1]  # 分配每个图像到训练或测试集
    rnd.shuffle(iFolder)  # 随机打乱顺序

    # 生成合成文本
    strings = []
    if args.input_file != '':
        print("使用指定文件 ", args.input_file)
        strings = create_strings_from_file(args.input_file, args.count, args.min_char, args.max_char)
    elif args.random_sequences:
        print("使用随机序列")
        strings = create_strings_randomly(args.length, args.random, args.count,
                                          args.include_letters, args.include_numbers, args.include_symbols, args.language)
        if args.include_symbols or not any([args.include_letters, args.include_numbers, args.include_symbols]):
            args.name_format = 2  # 自动设置名称格式以兼容特殊字符
    else:
        print("使用字典中的字符串")  # 此处我们使用这种方式
        strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)

    string_count = len(strings)
    print('string_count: ' + str(string_count))

    # 其他功能的设置，例如斜体、颜色等
    skew = []
    distort = []
    for l in strings:
        slen = len(l)
        if slen < 5:
            skew.append(7)
            distort.append(1)
        elif slen < 10:
            skew.append(3)
            distort.append(1)
        else:
            skew.append(0)
            distort.append(0)

    cursive = [0] * string_count  # 标记是否斜体
    for i in range(5 * wc, 7 * wc):
        cursive[i] = 15

    color, bgcolor = read_colorcomb("/home/jw/data/ocrdata/color_gray.txt")  # 读取颜色组合
    num_color = len(color)
    back = [1] * num_color  # 背景类型设置
    back[0] = 0
    back[1] = 0

    styles = string_count * [0]  # 样式设置

    # 生成合成文本的循环
    for cycle in range(1):
        with (Path(args.output_dir + "/" + outfolder[0] + ".txt")).open('w', encoding="utf8") as f0, \
             (Path(args.output_dir + "/" + outfolder[1] + ".txt")).open('w', encoding="utf8") as f1:
            for i in range(string_count):  # 创建标签文本文件
                folder_index = int(i / num_maxfile)
                if iFolder[i] == 0:
                    f0.write(f"{outfolder[0]}/{folder_index}/{str(i).zfill(num_digit)}.jpg\t{strings[i]}\n")
                else:
                    f1.write(f"{outfolder[1]}/{folder_index}/{str(i).zfill(num_digit)}.jpg\t{strings[i]}\n")

        p = Pool(args.thread_count)  # 使用多进程生成图像文件
        for _ in tqdm(p.imap(
            FakeTextDataGenerator.generate_from_tuple,
            zip(
                [i for i in range(0, string_count)],
                strings,
                [fonts[int(i / wc)] for i in range(0, string_count)],  # 分配字体
                [args.output_dir + "/" + outfolder[iFolder[i]] + "/" + str(int(i / num_maxfile)) for i in range(string_count)],
                [cursive[i] for i in range(string_count)],
                [args.format] * string_count,
                [args.extension] * string_count,
                [skew[i] for i in range(string_count)],
                [args.random_skew] * string_count,
                [args.blur] * string_count,
                [args.random_blur] * string_count,
                [back[i % num_color] for i in range(0, string_count)],  # 背景类型
                [args.distortion] * string_count,
                [args.distortion_orientation] * string_count,
                [args.handwritten] * string_count,
                [args.name_format] * string_count,
                [args.width] * string_count,
                [args.alignment] * string_count,
                [color[i % num_color] for i in range(0, string_count)],  # 文本颜色
                [args.orientation] * string_count,
                [args.space_width] * string_count,
                [args.margins] * string_count,
                [args.fit] * string_count,
                [args.bbox] * string_count,
                [args.label_only] * string_count,
                [bgcolor[i % num_color] for i in range(0, string_count)],  # 背景颜色
                [0] * string_count,  # 文本描边宽度
                [''] * string_count  # 描边颜色
            )
        ), total=args.count):
            pass
        p.terminate()
        rnd.shuffle(iFolder)  # 随机化文件夹分配

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise