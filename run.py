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
        default="/home/jw/data/ocr/kor3/",
    )    
    parser.add_argument(
        "-i", "--input_file",
        type=str, nargs="?",
        help="When set, this argument uses a specified text file as source for the text",
        default=""
    )
    parser.add_argument(
        "-l", "--language",
        type=str, nargs="?",
        help="The language to use, should be fr (French), en (English), es (Spanish), de (German), or cn (Chinese), or ko (Korean)",
        default="ko" ###
    )
    parser.add_argument(
        "-nd", "--new_dict",
        action="store_true",
        help="Make new dictionary file in \'dicts\' directory",
        default=False
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
        default=96,
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
        default=0
    )
    parser.add_argument(
        "-do", "--distortion_orientation",
        type=int, nargs="?",
        help="Define the distortion's orientation. Only used if -d is specified. 0: Vertical (Up and down), 1: Horizontal (Left and Right), 2: Both",
        default=2
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
        default=False
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
    return parser.parse_args()

def make_dict(lang, inp):
    """
        Read input file and make dictionnary file
    """
    d = set()
    r = re.compile(' +')
    with open(inp, 'r', encoding="utf8") as f:
        for line in f:
            for token in re.sub(r, ' ', line.strip()).split(' '):
                d.add(token)

    with (Path('/home/jw/data/ocr/kor3') / (lang + '_new.txt')).open('w', encoding="utf8", errors='ignore') as f:
        for token in d:
            f.write(token+'\n')

def load_fonts(lang):
    return [str(font) for font in (Path('/home/jw/code/ocrdata/fonts') / lang).glob('*')]

def load_dict(lang):
    lang_dict = []   ### change the input ko.txt file  
    # dict_file = '/home/jw/data/ocr/kor3/symbols.txt' # test1, train1
    # dict_file = '/home/jw/data/ocr/kor3/eng input.txt' # test2, train2
    dict_file = '/home/jw/data/ocr/kor3/kor nov11.txt' # test3, train3
    with (Path(dict_file)).open('r', encoding="utf8", errors='ignore') as d:
        lang_dict = [l for l in d.read().splitlines() if len(l) > 0]
    return lang_dict

def main():
    # Argument parsing
    args = parse_arguments()
    print(args.output_dir)

    # print(args.new_dict)
    if args.new_dict:
        make_dict(args.language, args.input_file)

    # Creating word list
    lang_dict = load_dict(args.language)

    # Create font (path) list
    if not args.font:
        fonts = load_fonts(args.language)
    else:
        if Path(args.font).exists():
            fonts = [args.font]
        else:
            sys.exit("Cannot open font")

    wc = len(lang_dict)
    fc = len(fonts)
    args.count = wc * fc
    print('lang_dict: ' , str(wc)) # # of words in ko.txt
    print('fonts: ' , str(fc))     # # of fonts
    print('count:' + str(args.count))

    # Set train/test ratio
    num_test = int(args.count/10)
    num_train = args.count - num_test
    # iFolder = args.count*[0] # for testing only
    iFolder = num_train*[0] + num_test*[1]
    rnd.shuffle(iFolder)    

    # for i in range (fc):
    #     print(fonts[i])
    
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
        print("4. use strings from dict")
        strings = create_strings_from_dict(args.length, args.random, args.count, lang_dict)

    string_count = len(strings)
    print('string_count: '+str(string_count))
    
    ### Create the output directory if it does not exist.
    folder = ['train3','test3']    
    try:
        Path(args.output_dir+'/'+folder[0]).mkdir(exist_ok=True)
        Path(args.output_dir+'/'+folder[1]).mkdir(exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
  
    num_styles = 17
    pre = ['0_bw','1_sw','2_rw','3_wr','4_wb','5_ws','6_by','7_bt','8_bg','9_is','10_it','11_gg',
           '12_ob','13_oy','14_or','15_odt','16_ows']
    color = ['#282828','#0781de','#d11204','#FFFFFF','#FFFFFF','#FFFFFF','#282828','#282828','#282828','#ebe7c5','#ebe7c5','#55d97c',
             '#FFFFFF','#e8e23f','#d11204','#FFFFFF','#FFFFFF']       
    background = [0,0,0,1,1,1,1,1,1,1,1,1,
                  0,0,0,1,1]  
    bgcolor = ['','','','#d11204','#282828','#0781de','#e8e23f','#dbbe8c','#55d97c','#0781de','#dbbe8c','#888888',
               '','','','#dbbe8c','#0781de']
    skwidth = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6, 6, 6, 6]
    skcolor = ['','','','','','','','','','','','','#282828','#282828','#282828','#07337a','#d11204']

    for j in range(4):        
        if j == 0:
            k = 0
        else:
            k = rnd.randint(1,16)

        for i in range (string_count):  # 각 이미지마다 라벨 텍스트 파일 생성
            with (Path(args.output_dir+"/"+folder[iFolder[i]]+"/"+pre[k]+"_"+str(i)+".txt")).open('w', encoding="utf8") as f:
                f.write("{}".format(strings[i]))

        p = Pool(args.thread_count)     # Fake Text 이미지 파일 저장하기 
        
        for _ in tqdm(p.imap(
            FakeTextDataGenerator.generate_from_tuple,
            zip(
                [i for i in range(0, string_count)],
                strings,
                [fonts[int(i/wc)] for i in range(0, string_count)], #[fonts[rnd.randrange(0, len(fonts))] for _ in range(0, string_count)],
                [args.output_dir+"/"+folder[iFolder[i]] for i in range(string_count)],
                [pre[k]] * string_count,
                [args.format] * string_count,
                [args.extension] * string_count,
                [args.skew_angle] * string_count,
                [args.random_skew] * string_count,
                [args.blur] * string_count,
                [args.random_blur] * string_count,
                [background[k]] * string_count,   # background type 0: Gaussian Noise, 1: Plain color, 2: Quasicrystal, 3: Pictures"
                [args.distortion] * string_count,
                [args.distortion_orientation] * string_count,
                [args.handwritten] * string_count,
                [args.name_format] * string_count,
                [args.width] * string_count,
                [args.alignment] * string_count,
                [color[k]] * string_count, # text color black 282828 darkblue 07337a yellow e8e23f darkyellow 07337a  ivory ebe7c5 green 55d97c
                [args.orientation] * string_count,
                [args.space_width] * string_count,
                [args.margins] * string_count,
                [args.fit] * string_count,
                [args.bbox] * string_count,
                [args.label_only] * string_count,
                [bgcolor[k]]* string_count,  # background color : activated when background type is 1 tan dbbe8c red d11204 sky 0781de tan dbbe8c 
                [skwidth[k]]* string_count,          # stroke width
                [skcolor[k]]* string_count   # stroke color
            )
        ), total=args.count):
            pass
        p.terminate()    

    # if args.name_format == 2:
    #     # Create file with filename-to-label connections
    #     with (Path(args.output_dir+"/"+folder[0]+".txt")).open('w', encoding="utf8") as f0:
    #         with (Path(args.output_dir+"/"+folder[1]+".txt")).open('w', encoding="utf8") as f1:
    #             for i in range(string_count):
    #                 file_name = str(i) + "." + args.extension
    #                 if iFolder[i] == 0:
    #                     f0.write("{}\t{}\n".format(folder[0]+'/'+file_name, strings[i]))
    #                 else:
    #                     f1.write("{}\t{}\n".format(folder[1]+'/'+file_name, strings[i]))

    # total_data = []
    # imgs = Path(args.output_dir+"/").glob('*.jpg')

    # for img in imgs:
    #     pkl = img.with_suffix('.pkl')
    #     with pkl.open('rb') as f:
    #         data = pickle.load(f)

    #     this_data = {
    #         'fn' : img.name,
    #         'charBB' : data['charBB'],
    #         'txt' : data['txt']
    #     }
    #     total_data.append(this_data)

    # with (Path(args.output_dir) / 'gt.pkl').open('wb') as gt:
    #     pickle.dump(total_data, gt)
    # print(f'{len(total_data)} data merged!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise
