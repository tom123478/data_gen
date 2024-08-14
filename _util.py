from pathlib import Path
import random as rnd
import errno
from PIL import Image
import os
import string

def showimage(): # Open and show an image
    imfile = '/home/jw/data/ocr/kor3/train2/15_odt_1101.jpg'
    im = Image.open(imfile)
    im.show()

# showimage()

def resize32(inputfolder, outfolder): # resize to 32 pixel height
    try:
        os.makedirs(outfolder)
    except:
        print("folder already exists")

    dir3 = os.listdir(inputfolder)
    numfile= 0
    for i, item in enumerate(dir3):
        imfile = inputfolder + item
        
        # imfile2 = outfolder + os.path.splitext(item)[0] + ".jpg"
        # if os.path.isfile(imfile2) == False:
            # print(imfile2)
        if(os.path.splitext(item)[1] == ".jpg"):
            try:
                im = Image.open(imfile)
            except IOError:
                print("IO Error", imfile)
            else:             
                width, height = im.size
                ratio = 32 / height
                if ratio<1:
                    width2 = int(width * ratio)
                    height2 = int(height * ratio)
                    im2 = im.resize((width2, height2))
                    im2.save(imfile)
                    numfile +=1   
    print(numfile)         

# resize32("/home/jw/data/easyocr/en/val1/", "/home/jw/data/easyocr/en/val1/")

def words_from_numbers(): # write numbers up to 10-digit : 2200 numbers
    outfile = '/home/jw/data/ocrdata/words num.txt'
    total = 0
    with (Path(outfile)).open('w', encoding="utf-8") as f:
        numitem = 300
        for i in range(100):
            f.write("{}\n".format(i))
            total += 1

        for nlen in range(3,10):
            # print (nlen)            
            for _ in range(numitem):
                random_number = rnd.randint(10**(nlen-1),10**(nlen))
                f.write("{:,}\n".format(random_number))
                total += 1
    print(total)
    
# words_from_numbers()

def generate_random_email(): # generate 2800 random emails from characters & symbols
    with open('/home/jw/data/ocrdata/dict en.txt', 'r', encoding='utf-8') as f:
        char = [' '.join(l.strip().split()) for l in f]        
    char_list = list(char[0])
    # print(char_list)

    character_counts = {}
    for char in char_list:
        character_counts[char] = 0

    infile = '/home/jw/data/ocrdata/domain.txt'
    outfile = '/home/jw/data/ocrdata/words email.txt'
    with open(infile, 'r', encoding='utf-8') as f:
        domains = [' '.join(l.strip().split()) for l in f]

    words = []
    numitem = 2800
    with (Path(outfile)).open('w', encoding="utf-8") as f:
        for _ in range(numitem):
            # Randomly choose a prefix and domain
            domain = rnd.choice(domains)
            nlen = rnd.randint(4,15)
            # Generate a random string of letters and digits for the username
            username = ''.join(rnd.choice(string.ascii_letters + string.digits + "_") for _ in range(nlen))

            # Combine username and domain to form the email
            email = f"{username}@{domain}"
            f.write("{}\n".format(email))
            words.append(email)
        # Iterate through each word in the list
    
    for word in words:
        # Iterate through each character in the word
        for char in word:
            # Increment the count for the character in the dictionary
            if char in character_counts:
                character_counts[char] += 1
            else:
                character_counts[char] = 1
    for char, count in character_counts.items():
        print(f"Character '{char}' occurs {count} times.")
 
# generate_random_email()

def combine_words(): # combine all words files and make stat
    # file_dict = '/home/jw/data/ocrdata/dict en.txt'
    # txt_files = ['/home/jw/data/ocrdata/words num.txt',
    #              '/home/jw/data/ocrdata/words email.txt',
    #              '/home/jw/data/ocrdata/source en 10000.txt',
    #              '/home/jw/data/ocrdata/words en 10000.txt',
    #              '/home/jw/data/ocrdata/words en random.txt'
    #              ]    
    # outfile = '/home/jw/data/ocrdata/words en all.txt' 
    # file_stat = '/home/jw/data/ocrdata/_stat.txt'

    file_dict = '/home/jw/data/ocrdata/dict ko.txt'
    txt_files = [
                #  '/home/jw/data/ocrdata/words ko nov.txt',
                 '/home/jw/data/ocrdata/words ko random.txt'
                 ]    
    outfile = '/home/jw/data/ocrdata/words ko all.txt' 
    file_stat = '/home/jw/data/ocrdata/_stat ko.txt'
    
    with open(file_dict, 'r', encoding='utf-8') as f:
        char = [' '.join(l.strip().split()) for l in f]        
    char_list = list(char[0])
    # print(char_list)
    
    max = 25
    words = []
    for inputfile in txt_files:
        with open(inputfile, 'r', encoding='utf-8') as f:
            lines = [' '.join(l.strip().split()) for l in f]
            lines = [l[:] for l in lines if len(l) > 0]            
            for l in lines:
                line = l.split()
                for w in line:
                    nw = len(w)
                    w2 = ''
                    for i in range(min(nw, max)):
                        if w[i] in char_list:
                            w2 = w2 + w[i]
                    if len(w2) < max and len(w2) > 0:
                        words.append(w2)
    # Get unique words only
    # words.sort()
    # word2 = list(dict.fromkeys(words))
    print(len(words))

    character_counts = {}
    for char in char_list:
        character_counts[char] = 0

    # Iterate through each word in the list
    for word in words:
        # Iterate through each character in the word
        for char in word:
            # Increment the count for the character in the dictionary
            if char in character_counts:
                character_counts[char] += 1
            else:
                character_counts[char] = 1
    with open(file_stat, 'w', encoding='utf-8') as f:
        for char, count in character_counts.items():
            f.write(f"'{char}'\t{count}\n")

    # rnd.shuffle(word2)
    with open(outfile, 'w', encoding='utf-8') as fo:
        for w in words:
            fo.write(w +"\n") 

# combine_words()

def words_from_words(): # add random symbols to words list
    with open('/home/jw/data/ocrdata/dict en.txt', 'r', encoding='utf-8') as f:
        char = [' '.join(l.strip().split()) for l in f]        
    char_list = list(char[0])
    # print(char_list)

    txt_files = [ '/home/jw/data/ocrdata/source en 10000.txt' ]    
    outfile = '/home/jw/data/ocrdata/words en 10000.txt' 
    pre = ['#','$','(','<','"','\'']
    mid = ['%','*','+','/','=','-']
    suf = ['&',')','^',':','>','"','\'','.',',','?','!']
    max = 25
    words = []
    for inputfile in txt_files:
        with open(inputfile, 'r', encoding='utf-8') as f:
            lines = [' '.join(l.strip().split()) for l in f]
            lines = [l[:] for l in lines if len(l) > 0]            
            for l in lines:
                line = l.split()
                for w in line:
                    nw = len(w)
                    w2 = ''
                    W = w.capitalize()
                    for i in range(0, min(nw, max)):
                        if W[i] in char_list:
                            w2 = w2 + W[i]
                    if len(w2) < max and len(w2) > 1:
                        words.append(w2)
    words.sort()
    word2 = list(dict.fromkeys(words))
    # print(word2)
    print(len(word2))
    # rnd.shuffle(word2) 

    words = []
    for i, w in enumerate(word2):
        if(i%4 == 0):
            words.append(rnd.choice(pre) + w + rnd.choice(suf))
        elif(i%4 == 1):
            words.append(rnd.choice(pre) + w + rnd.choice(suf))
        elif(i%4 == 2):
            words.append(rnd.choice(mid) + w+ rnd.choice(suf))
        else:
            words.append(w[:1] + rnd.choice(mid) + w[1:])

    character_counts = {}
    for char in char_list:
        character_counts[char] = 0

    # Iterate through each word in the list
    for word in words:
        # Iterate through each character in the word
        for char in word:
            # Increment the count for the character in the dictionary
            if char in character_counts:
                character_counts[char] += 1
            else:
                character_counts[char] = 1
    with open('/home/jw/data/ocrdata/_stat2.txt', 'w', encoding='utf-8') as f:
        for char, count in character_counts.items():
            f.write(f"'{char}'\t{count}\n")

    with open(outfile, 'w', encoding='utf-8') as fo:
        for w in words:
            fo.write(w[:max] +"\n")             

# words_from_words()
                
def phrases_from_novel(): # get phrases within a fixed length
    txt_file = '/home/jw/code/ocrdata/test.txt'
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

# words_from_novel()

def delete_dup(): # delete duplicate words and make unique words list
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

def combine_txt0(): # train0,train1,...을 특정 비율로 train.txt, val.txt로 통합해줌 
    output_dir = "/home/jw/data/ocrdata/en/"
    folder = ['val','train']
    num_folder = len(folder)
    num_case = 2    ### specify how many cases to include  

    for i in range(num_folder): # val, train
        with (Path(output_dir+folder[i]+".txt")).open('w', encoding="utf-8") as fo:
            for j in range(0 , num_case):
                dirn = folder[i] + str(j) # train0, train1, train2....
                dir = output_dir + dirn 
                txtfiles = [str(file) for file in (Path(dir)).glob('*.txt')]
                num_file = len(txtfiles)
                print(dir + ": " + str(num_file))
                npicked = 0

                if(j == 0):
                    index = num_file*[1]
                elif j == 1: # only pick half of the items 
                    num_get = int(num_file/2)
                    num_not = num_file - num_get
                    index = num_not*[0] + num_get*[1]
                    rnd.shuffle(index)  
                else:        # only pick 1/6 of the items 
                    num_get = int(num_file/6)
                    num_not = num_file - num_get
                    index = num_not*[0] + num_get*[1]
                    rnd.shuffle(index)

                for k in range(num_file):
                    if(index[k] == 1):
                        txtfile = txtfiles[k]
                        name = Path(txtfile).stem
                        jpgfile = Path(dir + '/' + name + '.jpg')
                        # jpgfile2 = Path(output_dir + folder[i] + '/' + name + '.jpg')
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

def combine_txt(): # train0,train1,을 train.txt, val.txt로 통합해줌
    output_dir = "/home/jw/data/ocrdata/ko/"
    folder = ['val','train']
    num_folder = len(folder)
    num_case = 4    ### specify how many cases to include  

    for i in range(num_folder): # val, train
        with (Path(output_dir+folder[i]+".txt")).open('w', encoding="utf-8") as fo:
            for j in range(0 , num_case):
                dirn = folder[i] + str(j+1) # train1, train2....
                dir = output_dir + dirn 
                txtfile = dir + ".txt"
                with (Path(txtfile)).open('r', encoding="utf-8") as f:                    
                    for l in f:
                        fo.write(l)

# combine_txt()
        
def unique_characters(words): # functions to extract unique characters from words list
    unique_chars = set()  # Using a set to store unique characters
    for word in words:
        unique_chars.update(set(word))  # Add characters of each word to the set
    return unique_chars
        
def make_dict_from_txt(): # find and write unique characters from txt file
    
    filename = "/home/jw/data/easyocr/words ko_.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        word_list = [' '.join(l.strip().split()) for l in f]
    # print(word_list)

    unique_chars = unique_characters(word_list)
    unique_chars = sorted(unique_chars)
    print("Unique characters:", unique_chars)

    with open("/home/jw/data/easyocr/dict ko.txt", 'w', encoding='utf-8') as fo:
        for ch in unique_chars:
            fo.write("{}".format(ch))
    fo.close()

# make_dict_from_txt()

def make_dict(): # Make dict file (unique characters in one line)
    file_i = "/home/jw/data/ocrdata/char ko.txt"
    file_o = "/home/jw/data/ocrdata/dict ko.txt"

    with open(file_i, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]
    f.close()

    with open(file_o, 'w', encoding='utf-8') as fo:
        for l in lines:
            fo.write("{}".format(l))
    fo.close()

# make_dict()

def make_charset(): # Make char file (unique characters in each line)
    file_i = "/home/jw/data/easyocr/char ko.txt"
    file_o = "/home/jw/code/synthtiger/resources/charset/alphanum_special_ko.txt"

    with open(file_i, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]
    f.close()

    with open(file_o, 'a', encoding='utf-8') as fo:
        for l in lines:
            fo.write("{}".format(l))
    fo.close()

# make_charset()
    
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

# color_font, color_back = read_colorcomb("/home/jw/data/ocrdata/color_bw.txt")
# print(color_font)
# print(color_back)

def color2grey(): # convert color image to grayscale and save it
    for i in range(32):
        infile = '/home/jw/data/ocrdata/en/train0/0/' + str(i).zfill(6) + '.jpg'
        outfile = '/home/jw/data/ocrdata/en/train0/0/'+ str(i).zfill(6) + '_.jpg'
        im = Image.open(infile)
        gray = im.convert('L')
        gray.save(outfile)
        
# color2grey()

def rotate_img(imfile):
    folder = os.path.dirname(imfile)
    file_name, ext = os.path.splitext(os.path.basename(imfile))
    
    try:
        im = Image.open(imfile)
    except IOError:
        print("IO Error", imfile)
    else:
        im2 = im.rotate(-90,expand=1)
        im2.save(imfile)
 
# rotate_img('/home/jw/data/test/청구서.jpg')