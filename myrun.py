from pathlib import Path
import random as rnd
import errno
from PIL import Image
import os

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
    with (Path('C:/Data/kor/kor3/korean_dict_symbol.txt')).open('r', encoding="utf-8", errors='ignore') as d:
        dict = [l for l in d.read().splitlines() if len(l) > 0]
    n_dict = len(dict)    
    print(n_dict)

    with (Path('C:/Data/kor/kor3/num_symbol.txt')).open('w', encoding="utf-8") as f:
        
        rnd.shuffle(dict)
        for length in range(2,16) :
            lines = int(n_dict/length)
            remain = n_dict%length
            print(str(length)+'x'+ str(lines) +' + '+ str(remain))        
            for i in range(lines):
                if length < 100:  
                    for j in range(length):
                        f.write("{}".format(dict[i*length+j]))
                    f.write("\n")
                elif length < 200: #
                    for j in range(4):
                        f.write("{}".format(dict[i*length+j]))                   
                    for j in range(4,length):
                        f.write("{}".format(dict[i*length+j]))
                    f.write("\n")
                else:           # 
                    for j in range(6):
                        f.write("{}".format(dict[i*length+j]))
                    f.write(" ")
                    for j in range(6,length):
                        f.write("{}".format(dict[i*length+j]))
                    f.write("\n")

            # for j in range(remain):
            #     f.write("{}".format(dict[lines*length+j]))
            # f.write("\n")
    f.close()

# words_from_dicts()
                
def words_from_novel():
    file = ''

# words_from_novel()              

def combine_txt():     
    output_dir = "C:/Data/kor/out/"
    folder = ['test','train']
    num_folder = len(folder)
    num_case = 2    ### specify how many cases to include
    ver = [0, 1]    #   세로 데이터 vertical text 표시해줌. 세로이미지는 -90도 돌려줌 (그런데 이게 필요한가?)

    # Create the directory if it does not exist.
    try:
        Path(output_dir+'/'+folder[0]).mkdir(exist_ok=True)
        Path(output_dir+'/'+folder[1]).mkdir(exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for i in range(num_folder):
        with (Path(output_dir+folder[i]+".txt")).open('w', encoding="utf-8") as fo:
            for j in range(0 , num_case):
                dir = output_dir + folder[i] + str(j+1)
                vert = ver[j]
                txtfiles = [str(file) for file in (Path(dir)).glob('*.txt')]
                num_file = len(txtfiles)
                print(dir + ": " + str(num_file))

                for k in range(num_file):
                    txtfile = txtfiles[k]
                    name = Path(txtfile).stem
                    jpgfile = Path(dir + '/' + name + '.jpg')
                    jpgfile2 = Path(output_dir + folder[i] + '/' + name + '.jpg')
                    if jpgfile.is_file():
                        try:
                            im = Image.open(jpgfile)
                            width, height = im.size

                            if vert == 1:                                
                                im2 = im.rotate(90, expand=1)
                                im2.save(jpgfile2)
                            else:
                                im.save(jpgfile2)

                            with (Path(txtfile)).open('r', encoding="utf-8") as fin:
                                line = fin.readline().strip('\n')
                                fo.write("{}/{}.jpg\t{}\n".format(folder[i],name,line))
                                # print(folder[i] + '/' +  name + '.jpg' + '\t' + line)
                            fin.close()
                        except IOError:
                            print("IO Error", jpgfile)                   
        fo.close()

# combine_txt()



