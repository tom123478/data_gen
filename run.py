import argparse
import os, errno
import random as rnd
import re
import sys
import pickle

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
    margins = margin.split(',')
    if len(margins) == 1:
        return [margins[0]] * 4
    return [int(m) for m in margins]

def parse_arguments():
    """
        Parse the command line arguments of the program.
    """

    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')

    parser.add_argument(
        "--output_dir",
        type=str, nargs="?",
        help="The output directory",
        default="/home/jw/data/ocrdata/en/",
    )    
    parser.add_argument(
        "-i", "--input_file",
        type=str, nargs="?",
        help="When set, this argument uses a specified text file as source for the text",
        default=""
    )
    parser.add_argument(
        "-c", "--count",
        type=int, nargs="?",
        help="The number of images to be created. # of words x # of fonts",
        default=10000
    )
    parser.add_argument(
        "-rs", "--random_sequences",
        action="store_true",
        help="Use random sequences as the source text for the generation. Set '-let','-num','-sym' to use letters/numbers/symbols. If none specified, using all three.",
        default=False
    )
    parser.add_argument(
        "-let", "--include_letters",
        action="store_true",
        help="Define if random sequences should contain letters. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-num", "--include_numbers",
        action="store_true",
        help="Define if random sequences should contain numbers. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-sym", "--include_symbols",
        action="store_true",
        help="Define if random sequences should contain symbols. Only works with -rs",
        default=False
    )
    parser.add_argument(
        "-w", "--length",
        type=int, nargs="?",
        help="Define how many words should be included in each generated sample. If the text source is Wikipedia, this is the MINIMUM length",
        default=1
    )
    parser.add_argument(
        "-r", "--random",
        action="store_true",
        help="Define if the produced string will have variable word count (with --length being the maximum)",
        default=False
    )
    parser.add_argument(
        "-f", "--format",
        type=int, nargs="?",
        help="Define the height of the produced images if horizontal, else the width",
        default=64,
    )
    parser.add_argument(
        "-t", "--thread_count",
        type=int, nargs="?",
        help="Define the number of thread to use for image generation",
        default=1,
    )
    parser.add_argument(
        "-e", "--extension",
        type=str, nargs="?",
        help="Define the extension to save the image with",
        default="jpg",
    )
    parser.add_argument(
        "-k", "--skew_angle",
        type=int, nargs="?",
        help="Define skewing angle of the generated text. In positive degrees",
        default=1,
    )
    parser.add_argument(
        "-rk", "--random_skew",
        action="store_true",
        help="When set, the skew angle will be randomized between the value set with -k and it's opposite",
        default=True,
    )
    parser.add_argument(
        "-bl", "--blur",
        type=int, nargs="?",
        help="Apply gaussian blur to the resulting sample. Should be an integer defining the blur radius",
        default=1,
    )
    parser.add_argument(
        "-rbl", "--random_blur",
        action="store_true",
        help="When set, the blur radius will be randomized between 0 and -bl.",
        default=True,
    )    
    parser.add_argument(
        "-hw", "--handwritten",
        action="store_true",
        help="Define if the data will be \"handwritten\" by an RNN",
        default=False,
    )
    parser.add_argument(
        "-na", "--name_format",
        type=int,
        help="Define how the produced files will be named. 0: [TEXT]_[ID].[EXT], 1: [ID]_[TEXT].[EXT] 2: [ID].[EXT] + one file labels.txt containing id-to-label mappings",
        default=3,
    )
    parser.add_argument(
        "-d", "--distortion",
        type=int, nargs="?",
        help="Define a distortion applied to the resulting image. 0: None (Default), 1: Sine wave, 2: Cosine wave, 3: Random",
        default=1  #select 1 or 2, never 3
    )
    parser.add_argument(
        "-do", "--distortion_orientation",
        type=int, nargs="?",
        help="Define the distortion's orientation. Only used if -d is specified. 0: Vertical (Up and down), 1: Horizontal (Left and Right), 2: Both",
        default=0 
    )
    parser.add_argument(
        "-wd", "--width",
        type=int, nargs="?",
        help="Define the width of the resulting image. If not set it will be the width of the text + 10. If the width of the generated text is bigger that number will be used",
        default=-1
    )
    parser.add_argument(
        "-al", "--alignment",
        type=int, nargs="?",
        help="Define the alignment of the text in the image. Only used if the width parameter is set. 0: left, 1: center, 2: right",
        default=1
    )
    parser.add_argument(
        "-or", "--orientation",
        type=int, nargs="?",
        help="Define the orientation of the text. 0: Horizontal, 1: Vertical",
        default=0
    )   
    parser.add_argument(
        "-sw", "--space_width",
        type=float, nargs="?",
        help="Define the width of the spaces between words. 2.0 means twice the normal space width",
        default=1.0
    )
    parser.add_argument(
        "-m", "--margins",
        type=margins, nargs="?",
        help="Define the margins around the text when rendered. In pixels",
        default=(5, 5, 5, 5)
    )
    parser.add_argument(
        "-fi", "--fit",
        action="store_true",
        help="Apply a tight crop around the rendered text",
        default=True
    )
    parser.add_argument(
        "-ft", "--font",
        type=str, nargs="?",
        help="Define font to be used",
        default = ''
    )
    parser.add_argument(
        "-bb", "--bbox",
        action="store_true",
        help="Draw bounding boxes of all letters. Also create a pickle file that \
              stores coordinate and text data.",
        default=False
    )
    parser.add_argument(
        "--label_only",
        action="store_true",
        help="Do not save bbox with pickle files"
    )
    parser.add_argument(
        "--min_char",
        type=int,
        help="Minimum number of character in a line",
        default=10
    )
    parser.add_argument(
        "--max_char",
        type=int, default=40,
        help="Maximum number of character in a line"
    )
    parser.add_argument( 
        "-tc", "--text_color",
        type=str, nargs="?",
        help="Define the text's color, should be either a single hex color or a range in the ?,? format.",
        default='#282828'
    )
    parser.add_argument(
        "-b", "--background",
        type=int, nargs="?",
        help="Define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Pictures",
        default=0,
    )
    parser.add_argument(
        "-l", "--language",
        type=str, nargs="?",
        help="The language to use, should be fr (French), en (English), es (Spanish), de (German), or cn (Chinese), or ko (Korean)",
        default="ko" ###
    )
    return parser.parse_args()

def read_colorcomb(file_i):
    with open(file_i, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]        
    f.close()
    
    num_comb = len(lines)
    color_font = []
    color_back = []
    # for i in range(num_comb):
    #     print(lines[i])
    for l in lines:
        line = l.split()
        color_font.append(line[0])
        color_back.append(line[1])

    return color_font, color_back

def load_fonts(lang):
    fontlist = [str(font) for font in (Path('/home/jw/code/ocrdata/fonts') / lang).glob('*')]
    n = 0
    for item in fontlist:
        print(str(n)+ " " + item)
        n += 1
    return fontlist

def load_dict(): ### change the input ko.txt file 
    lang_dict = []    
    # dict_file = '/home/jw/data/ocrdata/words en all.txt' # train0, val0
    dict_file = '/home/jw/data/ocrdata/words ko all.txt' # train2, val2
    # dict_file = '/home/jw/data/ocrdata/words test.txt'
   
    with (Path(dict_file)).open('r', encoding="utf8", errors='ignore') as d:
        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]

    # with (Path('/home/jw/data/easyocr/words en_.txt')).open('w', encoding="utf8") as fo:
    #     for l in lang_dict:
    #         if len(l)>25:
    #             fo.write("{}\n".format(l[:25]))
    #         else:
    #             fo.write("{}\n".format(l))
    # fo.close()
    return lang_dict

def main():
    args = parse_arguments()      # Argument parsing
        
    ### Create the output directory if it does not exist.
    outfolder = ['train2','val2']    
    try:
        Path(args.output_dir+'/'+outfolder[0]).mkdir(exist_ok=True)
        Path(args.output_dir+'/'+outfolder[1]).mkdir(exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Creating word list
    lang_dict = load_dict()

    # Create font (path) list
    if not args.font:
        fonts = load_fonts(args.language)
    else:
        if Path(args.font).exists():
            fonts = [args.font]
        else:
            sys.exit("Cannot open font")

    num_digit = 6
    num_maxfile = 10000
    wc = len(lang_dict)
    fc = len(fonts)
    args.count = wc * fc
    print(args.output_dir)
    print('lang_dict: ' , str(wc)) # # of words in ko.txt
    print('fonts: ' , str(fc))     # # of fonts
    print('count:' + str(args.count))

    nfolders = int(args.count/num_maxfile)
    for i in range(nfolders+1):
        # print(args.output_dir+"/"+outfolder[0]+"/"+str(i))
        Path(args.output_dir+'/'+outfolder[0]+'/'+str(i)).mkdir(exist_ok=True)
        Path(args.output_dir+'/'+outfolder[1]+'/'+str(i)).mkdir(exist_ok=True)   

    # Set train/test ratio
    num_test = int(args.count/10)
    num_train = args.count - num_test
    # iFolder = args.count*[0] # for testing only
    iFolder = num_train*[0] + num_test*[1]
    rnd.shuffle(iFolder)    

    
    # Creating synthetic sentences (or word)
    strings = []   
    if args.input_file != '':
        print("2. using ", args.input_file)
        strings = create_strings_from_file(args.input_file, args.count, args.min_char, args.max_char)
    elif args.random_sequences:
        print("3. using random sequence")
        strings = create_strings_randomly(args.length, args.random, args.count,
                                          args.include_letters, args.include_numbers, args.include_symbols, args.language)
        # Set a name format compatible with special characters automatically if they are used
        if args.include_symbols or True not in (args.include_letters, args.include_numbers, args.include_symbols):
            args.name_format = 2
    else:
        print("4. use strings from dict") # We're using this
        strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)

    string_count = len(strings)
    print('string_count: '+str(string_count))
    # print(strings)
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
  
    cursive = [0]*string_count
    for i in range(5*wc, 7*wc):
        cursive[i] = 15
  
    # number of styles = 1152
    color, bgcolor = read_colorcomb("/home/jw/data/ocrdata/color_gray.txt")
    num_color = len(color)
    back = [1]*num_color
    back[0] = 0 
    back[1] = 0

    # skwidth = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 6]
    # skcolor = ['','','','','','','','','','','','','#282828','#282828','#282828','#07337a','#d11204']
    styles = string_count*[0]
 
    # First cycle produces standard b/w image, other cycles produce random style images. 
    for cycle in range(1):  
        # for i in range (string_count): 
        #     styles[i] = cycle

        # if cycle > 0: # 랜덤으로 스타일 적용하고 싶을 때
        #     for i in range (string_count): 
        #         styles[i] = rnd.randint(1,16)
        with (Path(args.output_dir+"/"+outfolder[0]+".txt")).open('w', encoding="utf8") as f0:
            with (Path(args.output_dir+"/"+outfolder[1]+".txt")).open('w', encoding="utf8") as f1:
                for i in range (string_count):  # 라벨 텍스트 파일 생성
                    if iFolder[i] == 0:
                        f0.write("{}/{}/{}.jpg\t{}\n".format(outfolder[0],int(i/num_maxfile),str(i).zfill(num_digit),strings[i]))
                    else:
                        f1.write("{}/{}/{}.jpg\t{}\n".format(outfolder[1],int(i/num_maxfile),str(i).zfill(num_digit),strings[i]))

        p = Pool(args.thread_count)     # Fake Text 이미지 파일 저장하기 
        
        for _ in tqdm(p.imap(
            FakeTextDataGenerator.generate_from_tuple,
            zip(
                [i for i in range(0, string_count)],
                strings,
                [fonts[int(i/wc)] for i in range(0, string_count)], #[fonts[rnd.randrange(0, len(fonts))] for _ in range(0, string_count)],
                [args.output_dir+"/"+outfolder[iFolder[i]]+"/"+str(int(i/num_maxfile)) for i in range(string_count)],
                [cursive[i] for i in range(string_count)],
                [args.format] * string_count,
                [args.extension] * string_count,
                [skew[i] for i in range(string_count)] ,
                [args.random_skew] * string_count,
                [args.blur] * string_count,
                [args.random_blur] * string_count,
                [back[i%num_color] for i in range(0, string_count)],   # background type 0: Gaussian Noise, 1: Plain color, 2: Quasicrystal, 3: Pictures"
                [args.distortion] * string_count,
                [args.distortion_orientation] * string_count,
                [args.handwritten] * string_count,
                [args.name_format] * string_count,
                [args.width] * string_count,
                [args.alignment] * string_count,
                [color[i%num_color] for i in range(0, string_count)], # text color black 282828 darkblue 07337a yellow e8e23f darkyellow 07337a  ivory ebe7c5 green 55d97c
                [args.orientation] * string_count,
                [args.space_width] * string_count,
                [args.margins] * string_count,
                [args.fit] * string_count,
                [args.bbox] * string_count,
                [args.label_only] * string_count,
                [bgcolor[i%num_color] for i in range(0, string_count)],  # background color : activated when background type is 1 tan dbbe8c red d11204 sky 0781de tan dbbe8c 
                [0] * string_count,  # stroke width 0 or 6
                ['']*string_count   # stroke color
            )
        ), total=args.count):
            pass
        p.terminate()       
        rnd.shuffle(iFolder)     


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise
