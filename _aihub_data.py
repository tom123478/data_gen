import os
import json
from PIL import Image
from pathlib import Path

# AiHub 야외실제촬영 이미지 
datapath = "/home/jw/data/aihub/train/"
path1 = datapath + "image/2.책표지/"  # 이미지
path2 = datapath + "label/2.책표지/"  # 라벨

titles = ["가로형간판","01.총류","02.철학","03.종교","04.사회과학","05.자연과학","06.기술과학","07.예술","08.언어","09.문학","10.역사","11.기타"]
category = titles[8]  ### change for each iteration
folder1 = path1 + category + "/"
folder2 = path2 + category + "/"

mode = "train3" ### hard code
outimpath = datapath + "out/" + mode + "/temp/"

def jpg2png(): # save jpg images in folder1 to png format
    num = 0
    print(folder1 + " processing...")
    for file in Path(folder1).glob('*.jpg'):
        im = Image.open(file)
        newfile = file.parent/(file.stem + '.png')
        # print(file)
        im.save(newfile)
        num += 1
        if num%500 == 0: 
            print(num)
    print(str(num) + ' files finished')

def png2jpg(): # save png images in folder 1 to jpg format
    num = 0
    print(folder1 + " processing...")
    for file in Path(folder1).glob('*.png'):
        im = Image.open(file)
        newfile = file.parent/(file.stem + '.jpg')
        # print(file)
        im.save(newfile)
        num += 1
        if num%500 == 0: 
            print(num)
    print(str(num) + ' files finished')


def delete_image(num): # delete jpg or png files in folder1
    if num == 0:
        extension = '*.jpg'
    else:
        extension = '*.png'
    for file in Path(folder1).glob(extension):
        os.remove(file)
    print(folder1 + " " + extension, " deleted.")


def check_image_orientation(): # list vertical images in folder 1 and rotate 90 degrees
    dir2 = os.listdir(folder1)
    num = 0
    with open(folder1+"_vertical.txt", 'w', encoding="utf-8") as fo:
                    
        for i, item in enumerate(dir2):
            imfile = folder1 + item
            try:
                im = Image.open(imfile)
            except IOError:
                print("IO Error", imfile)
            else:
                width, height = im.size
                if height > width:
                    num += 1
                    print("Orientation not right: ", item, str(width), " x ", str(height))
                    fo.write(item+ "\n")
                    newfile = folder1 + item
                    im2 = im.rotate(90,expand=1)
                    im2.save(newfile)
        print(num, " files were vertically oriented")
    fo.close()


def read_label(file, prevtext): # read label json file and ignore if the text is same as previous text
    f = open(file, encoding='utf-8')
    data = json.load(f)
    texts = []
    boxes = []
    done = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for item in data["annotations"]:
        id = item["id"]
        text = item["text"]
        if id == 1:
            if text == prevtext:
                return texts, boxes, text
            else:
                text1 = text
        if 'x' not in text.lower(): # 한글일 경우에만 가능 xxx = text not available
            # print(item)
            # print(text)
            if done[id] == 0:
                texts.append(str(text))            
                box = item["bbox"]
                boxes.append(box)
                done[id] = 1
    f.close()
    return texts, boxes, text1


def cropimage_writetxt(imfile, outimpath, texts, boxes): # save cropped images of texts in outimpath
    filepath = os.path.splitext(imfile)[0]
    path = os.path.split(filepath)[0]
    file = os.path.split(filepath)[1]
    
    try:
        im = Image.open(imfile)
    except IOError:
        print("IO Error", imfile)
    else:
        width, height = im.size  
        min = 96      
 
        for i, text in enumerate(texts):
            file_jpg = file + "_" + str(i) + ".jpg"
            file_txt = file + "_" + str(i) + ".txt"    
            
            if os.path.isfile(outimpath + file_jpg) == False:
                box = boxes[i]
                x0 = box[0]/2
                y0 = box[1]/2
                dx = box[2]/2
                dy = box[3]/2
                x1 = x0 + dx
                y1 = y0 + dy
                if dx > dy:
                    dd = dy
                else:
                    dd = dx

                im2 = im.crop((int(x0),int(y0),int(x1),int(y1)))
                w, h = im2.size
                ratio = min/dd
                width2 = int(w * ratio)
                height2 = int(h * ratio)
                im3 = im2.resize((width2, height2))
                vratio = height2/width2
                
                if text[-1]==" ":
                    # print(file_jpg, "  ", text, ".")
                    text = text[:-1]
                with open(outimpath+file_txt, 'w', encoding="utf-8") as fo:
                    fo.write(mode + "/" + file_jpg + "\t" + text)
                fo.close()
                ntext = len(text)
                if ntext == 1:
                    im3.save(outimpath + file_jpg)
                elif vratio < 1.5:
                    im3.save(outimpath + file_jpg)
                    if vratio > 1 and len(text)==2:
                        print(file_jpg+ ": " + text)
                else:
                    im4 = im3.rotate(90,expand=1)
                    im4.save(outimpath + file_jpg)              
                # print(text+ " " + str((x0,y0, x1,y1)))                
                # print(imfile)


def text_subset(): # 
    try:
        os.makedirs(outimpath)
    except:
        print("Run text_subset ", folder1)  
    dir1 = os.listdir(folder2)
    prevtext = ""
    for i, item in enumerate(dir1):
        imfile = folder1 + os.path.splitext(item)[0] + ".jpg"
        if Path(imfile).exists():
            fname = folder2 + item
            # print(fname)
            texts, boxes, text1 = read_label(fname, prevtext)
            # print(texts)
            # print(boxes)
            cropimage_writetxt(imfile, outimpath, texts, boxes)
            prevtext = text1


# Step 1. Convert to png images (30분 정도 걸림) and delete jpg images.
# jpg2png()
# delete_image(0) 
        
# Step 2. Check if orientation is right. Manually realign image in correct orientation.
# check_image_orientation()
            
# Step 3. convert to jpg images and delete png images
# png2jpg()
# delete_image(1)    

# Step 4. Prepare SimpleDataset according to label/image pairs.
# text_subset()