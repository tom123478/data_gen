from pathlib import Path
import random as rnd
import errno
from PIL import Image
import os
import string

def character_count(): # writes stat about the occurence of each character in words file
    with open('/home/jw/data/ocrdata/dict en.txt', 'r', encoding='utf-8') as f:
        char = [' '.join(l.strip().split()) for l in f]        
    char_list = list(char[0])
    # print(char_list)
    character_counts = {}
    for char in char_list:
        character_counts[char] = 0

    txt_files = ['/home/jw/data/ocrdata/words en all.txt']
    for inputfile in txt_files:
        with open(inputfile, 'r', encoding='utf-8') as f:
            word2 = [' '.join(l.strip().split()) for l in f]

    # Iterate through each word in the list
    for word in word2:
        # Iterate through each character in the word
        for char in word:
            # Increment the count for the character in the dictionary
            if char in character_counts:
                character_counts[char] += 1
            else:
                character_counts[char] = 1
    
    with open('/home/jw/data/ocrdata/_stat.txt', 'w', encoding='utf-8') as f:
        for char, count in character_counts.items():
            f.write(f"'{char}'\t{count}\n")

# character_count()

def words_from_char(): # produce random words from characters
    inputfile = '/home/jw/data/ocrdata/dict en.txt' 
    outfile = '/home/jw/data/ocrdata/words en random.txt'
    statfile = '/home/jw/data/ocrdata/_stat1.txt'
    
    inputfile = '/home/jw/data/ocrdata/dict ko.txt' 
    outfile   = '/home/jw/data/ocrdata/words ko random.txt'
    statfile = '/home/jw/data/ocrdata/_stat ko random.txt'

    with (Path(inputfile)).open('r', encoding="utf-8", errors='ignore') as f:
        char = [' '.join(l.strip().split()) for l in f]
    dict = list(char[0])
    # print(len(dict))    
   
    words = []
    for wlen in range(1,11): # 10*3k=30k for ko
        for i in range(3000): # 10*1500=15k for en
            w = ''
            for i in range(wlen):
                w = w + rnd.choice(dict)
            words.append(w)

    for wlen in range(11,25): #14*1.5k=21 => total 51k
        for i in range(1500): # 15*500=7.5k for en => total 22k
            w = ''
            for i in range(wlen):
                w = w + rnd.choice(dict)
            words.append(w)    
    print(len(words)) 

    character_counts = {}
    for char in dict:
        character_counts[char] = 0
    
    for word in words:
        # Iterate through each character in the word
        for char in word:
            # Increment the count for the character in the dictionary
            if char in character_counts:
                character_counts[char] += 1
            else:
                character_counts[char] = 1
    with open(statfile, 'w', encoding='utf-8') as f:
        for char, count in character_counts.items():
            f.write(f"'{char}'\t{count}\n")
    with open(outfile, 'w', encoding='utf-8') as fo:
        for w in words:
            fo.write(w +"\n")  

# words_from_char()

def delete_not_dict():
    file_d = '/home/jw/data/ocrdata/dict ko all.txt'
    file_r = '/home/jw/data/ocr/kor3/kor nov11.txt'
    file_w = '/home/jw/data/ocrdata/words ko nov.txt'

    with (Path(file_d)).open('r', encoding="utf-8", errors='ignore') as f:
        char = [' '.join(l.strip().split()) for l in f]
    dictlist = list(char[0])
    # print(len(dict)) 

    words = []
    with open(file_r, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]
        print(len(lines))
        for l in lines:
            l2 = ''
            for w in l:
                if w in dictlist:
                    l2 = l2 + w
            words.append(l2)
    
    word2 = list(dict.fromkeys(words))
    print(len(word2))

    with open(file_w, 'w', encoding='utf-8') as fo:
        for w in word2:
            fo.write(w +"\n")   

# delete_not_dict()
def test():
    outfile = "/home/jw/data/ocrdata/_test.txt"
    txtfile = "/home/jw/data/ocrdata/char en.txt"
    with(Path(outfile)).open('w', encoding="utf-8") as fo:          
        with (Path(txtfile)).open('r', encoding="utf-8") as f:                    
            for l in f:
                fo.write(l)

test()