from pathlib import Path
import random as rnd
import errno
from PIL import Image
import os

def openimage():
    imfile = '/home/jw/data/ocr/kor3/train2/15_odt_1101.jpg'
    im = Image.open(imfile)
    im.show()

# openimage()


def resize600(inputfolder, outfolder): # resize to 600 pixel
    try:
        os.makedirs(outfolder)
    except:
        print("folder already exists")

    dir3 = os.listdir(inputfolder)
    for i, item in enumerate(dir3):
        imfile = inputfolder + item

        imfile2 = outfolder + os.path.splitext(item)[0] + ".png"
        if os.path.isfile(imfile2) == False:
            # print(imfile2)
            try:
                im = Image.open(imfile)
            except IOError:
                print("IO Error", imfile)
            else:
                width, height = im.size
                if width > height:
                    dd = height
                else:
                    dd = width
                ratio = 600 / dd
                width2 = int(width * ratio)
                height2 = int(height * ratio)
                im2 = im.resize((width2, height2))
                im2.save(imfile2)
                
def words_from_dicts():
    dict = []
    with (Path('/home/jw/data/ocr/kor3/korean only.txt')).open('r', encoding="utf-8", errors='ignore') as d:
        dict = [l for l in d.read().splitlines() if len(l) > 0]
    n_dict = len(dict)    
    print(n_dict)

    with (Path('/home/jw/data/ocr/kor3//kor word.txt')).open('w', encoding="utf-8") as f:
        
        rnd.shuffle(dict)
        numwords = 0
        for wlen in range(14,15) :
            lines = int(n_dict/wlen)
            remain = n_dict%wlen
            numwords += lines+1
            print(str(wlen)+'x'+ str(lines) +' + '+ str(remain))        
            for i in range(lines):
                for j in range(wlen):
                    f.write("{}".format(dict[i*wlen+j]))
                f.write("\n")
                
                # if wlen < 100:  
                #     for j in range(wlen):
                #         f.write("{}".format(dict[i*wlen+j]))
                #     f.write("\n")
                # elif wlen < 200: #
                #     for j in range(4):
                #         f.write("{}".format(dict[i*wlen+j]))                   
                #     for j in range(4,wlen):
                #         f.write("{}".format(dict[i*wlen+j]))
                #     f.write("\n")
                # else:           # 중간 띄어쓰기 도입
                #     for j in range(6):
                #         f.write("{}".format(dict[i*wlen+j]))
                #     f.write(" ")
                #     for j in range(6,wlen):
                #         f.write("{}".format(dict[i*wlen+j]))
                #     f.write("\n")

            for j in range(remain):
                f.write("{}".format(dict[lines*wlen+j]))
            f.write("\n")
    f.close()
    print(numwords)

# words_from_dicts()
                
def phrases_from_novel(): # get phrases within a fixed length
    txt_file = '/home/jw/code/ocrdata/texts/test.txt'
    max = 20
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]
        lines = [l[:] for l in lines if len(l) > 0]
        text = []
        for l in lines:
            llen = len(l)
            if llen < max:
                text.append(l)
            else:
                words = l.split()
                num = len(words[0])
                temp = words[0]
                nwords = len(words)

                for i in range(1, nwords): 
                    num = num + 1 + len(words[i])                                       
                    if num < max:
                        temp = temp + ' ' + words[i]                                             
                    else:                        
                        text.append(temp[:max])
                        temp = words[i]
                        num = len(words[i])
                text.append(temp[:max])
        print(text)
        f.close()

# phrases_from_novel()   

def words_from_novel(): # get unique words lists from novels

    with open('/home/jw/data/ocr/kor3/korean_dict_3.txt', 'r', encoding='utf-8') as f:
        kordict = [' '.join(l.strip().split()) for l in f]
    f.close()

    txt_files = [
                '/home/jw/code/ocrdata/texts/alice.txt',
                 '/home/jw/code/ocrdata/texts/button.txt',
                 '/home/jw/code/ocrdata/texts/carol.txt',
                 '/home/jw/code/ocrdata/texts/charles.txt',
                 '/home/jw/code/ocrdata/texts/esop.txt',
                 '/home/jw/code/ocrdata/texts/gatsby.txt',
                 '/home/jw/code/ocrdata/texts/great.txt',
                 '/home/jw/code/ocrdata/texts/grimm.txt',
                 '/home/jw/code/ocrdata/texts/kapka.txt',
                 '/home/jw/code/ocrdata/texts/long.txt',
                 '/home/jw/code/ocrdata/texts/prince.txt'
    ]
    max = 25
    words = []
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = [' '.join(l.strip().split()) for l in f]
            lines = [l[:] for l in lines if len(l) > 0]            
            for l in lines:
                line = l.split()
                for w in line:
                    nw = len(w)
                    w2 = ''
                    for i in range(nw):
                        if w[i] in kordict:
                            w2 = w2 + w[i]
                    if len(w2) < max and len(w2) >1:
                        words.append(w2)
            
        f.close()

    words.sort()
    word2 = list(dict.fromkeys(words))
    print(word2)
    print(len(word2))
    with open('/home/jw/data/ocr/kor3/kor nov11.txt', 'w', encoding='utf-8') as fo:
        for w in word2:
            fo.write(w +"\n")                
    fo.close()

# words_from_novel()

def delete_dup():
    with open('/home/jw/data/ocr/kor3/kor nov0.txt', 'r', encoding='utf-8') as f:
        words = [l for l in f]
    f.close()

    words.sort()
    word2 = list(dict.fromkeys(words))    
    print(len(words))
    print(len(word2))
    with open('/home/jw/data/ocr/kor3/kor novel.txt', 'w', encoding='utf-8') as fo:
        for w in word2:
            fo.write(w)                
    fo.close()
# delete_dup()

# test, train 폴더가 test1, test2, test3,.. 등 줌여러 개 있을 경우  
# PaddleOCR에서 필요한 simpledataset 형식으로 test.txt, train.txt로 만들어줌
def combine_txt():     
    output_dir = "/home/jw/data/ocr/kor3/"
    folder = ['test','train']
    num_folder = len(folder)
    num_case = 3    ### specify how many cases to include
    ver = [0, 0, 0]    #   세로 데이터 vertical text 표시해줌. 세로이미지는 -90도 돌려줌 (그런데 이게 필요한가?)

    # # Create the directory if it does not exist.
    # try:
    #     Path(output_dir+'/'+folder[0]).mkdir(exist_ok=True)
    #     Path(output_dir+'/'+folder[1]).mkdir(exist_ok=True)
    # except OSError as e:
    #     if e.errno != errno.EEXIST:
    #         raise

    for i in range(num_folder): # test, train
        with (Path(output_dir+"_"+folder[i]+".txt")).open('w', encoding="utf-8") as fo:
            for j in range(0 , num_case):
                dirn = folder[i] + str(j+1) # test1, test2, test3....
                dir = output_dir + dirn 
                # vert = ver[j]
                txtfiles = [str(file) for file in (Path(dir)).glob('*.txt')]
                num_file = len(txtfiles)
                print(dir + ": " + str(num_file))
                npicked = 0

                if(j == 0):
                    index = num_file*[1]
                elif j == 1: # only pick some of the items 
                    num_get = int(num_file/2)
                    num_not = num_file - num_get
                    index = num_not*[0] + num_get*[1]
                    rnd.shuffle(index)  
                else:
                    num_get = int(num_file/6)
                    num_not = num_file - num_get
                    index = num_not*[0] + num_get*[1]
                    rnd.shuffle(index)

                for k in range(num_file):
                    if(index[k] == 1):
                        txtfile = txtfiles[k]
                        name = Path(txtfile).stem
                        jpgfile = Path(dir + '/' + name + '.jpg')
                        jpgfile2 = Path(output_dir + folder[i] + '/' + name + '.jpg')
                        if jpgfile.is_file():
                            try:
                                # im = Image.open(jpgfile)
                                # width, height = im.size

                                # if vert == 1:                                
                                #     im2 = im.rotate(90, expand=1)
                                #     im2.save(jpgfile2)
                                # else:
                                #     im.save(jpgfile2)

                                with (Path(txtfile)).open('r', encoding="utf-8") as fin:
                                    line = fin.readline().strip('\n')
                                    fo.write("{}/{}.jpg\t{}\n".format(dirn,name,line))
                                    # print(folder[i] + '/' +  name + '.jpg' + '\t' + line)
                                    npicked += 1
                                fin.close()

                            except IOError:
                                print("IO Error", jpgfile)                   
                print(dirn, ": ", npicked)
        fo.close()

combine_txt()
        
def test():
    with open('/home/jw/data/ocr/kor3/korean_dict_3.txt', 'r', encoding='utf-8') as f:
        kordict = [' '.join(l.strip().split()) for l in f]
        # print(dict)
    f.close()
    words = []
    with open('/home/jw/data/ocr/kor3/test_sym', 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]
        lines = [l[:] for l in lines if len(l) > 0] 
        for l in lines:
            nl = len(l)
            w2 = ''
            for i in range(nl):
                if l[i] in kordict:
                    w2 = w2 + l[i]
            print(w2)
            if len(w2) < max and len(w2) >1:
                words.append(w2)
    f.close()

# test()



