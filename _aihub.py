import os
import json
import shutil
from PIL import Image
from pathlib import Path

# AiHub 야외실제촬영 이미지 
datapath = '/home/jw/data/aihub/'
# path0 = datapath + '[라벨]Training/2.책표지/'  # 라벨
# path1 = datapath + '[원천]Training/2.책표지/'  # 이미지
path0 = datapath + '[라벨]Validation/2.책표지/'  # 라벨
path1 = datapath + '[원천]Validation/2.책표지/'  # 이미지

titles = ['1.가로형간판','01.총류','02.철학','03.종교','04.사회과학','05.자연과학','06.기술과학','07.예술','08.언어','09.문학','10.역사','11.기타']
category = titles[11]  ### change for each iteration
labfolder = path0 + category + '/'
imgfolder = path1 + category + '/'

mode = 'val4' ### hard code 
outimpath = datapath + mode + '/'

def jpg2png(): # save jpg images in imgfolder to png format
    num = 0
    print(imgfolder + " processing...")
    for file in Path(imgfolder).glob('*.jpg'):
        im = Image.open(file)
        newfile = file.parent/(file.stem + '.png')
        # print(file)
        im.save(newfile)
        num += 1
        if num%500 == 0: 
            print(num)
    print(str(num) + ' files finished')

def png2jpg(): # save png images in imgfolder 1 to jpg format
    num = 0
    print(imgfolder + " processing...")
    for file in Path(imgfolder).glob('*.png'):
        im = Image.open(file)
        newfile = file.parent/(file.stem + '.jpg')
        # print(file)
        im.save(newfile)
        num += 1
        if num%500 == 0: 
            print(num)
    print(str(num) + ' files finished')

def delete_image(num): # delete jpg or png files in imgfolder
    if num == 0:
        extension = '*.jpg'
    else:
        extension = '*.png'
    for file in Path(imgfolder).glob(extension):
        os.remove(file)
    print(imgfolder + " " + extension, " deleted.")

def check_image_orientation(): # list vertical images in folder 1 and rotate 90 degrees
    dir2 = os.listdir(imgfolder)
    num = 0
    with open(imgfolder+"_vertical.txt", 'w', encoding="utf-8") as fo:
                    
        for i, item in enumerate(dir2):
            imfile = imgfolder + item
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
                    newfile = imgfolder + item
                    im2 = im.rotate(90,expand=1)
                    im2.save(newfile)
        print(num, " files were vertically oriented")
    fo.close()

def read_label(file, prevtext): # read label json file and ignore if the text is same as previous text
    f = open(file, encoding='utf-8')
    data = json.load(f)
    texts = []
    boxes = []
    done = [0]*100
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
            
            if len(text)>0 and done[id] == 0:                          
                box = item["bbox"]
                # print(box)
                if(box[0] is not None):                    
                    boxes.append(box)
                    texts.append(str(text))  
                done[id] = 1
    f.close()
    return texts, boxes, text1

def cropimage_writetxt(imfile, outimpath, category, txtfile, texts, boxes): # save cropped images of texts in outimpath
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
        verttxt = datapath + 'val_vert.txt'    ### change between train_vert / val_vert
        num = 0
        for i, text in enumerate(texts):
            file_jpg = file + "_" + str(i) + ".jpg"  
            path_jpg = category + "/" + file_jpg
            full_jpg = outimpath + path_jpg
            vertfile = outimpath + "vertical/" + file_jpg
            
            if Path(full_jpg).exists() == False and Path(vertfile).exists() == False:
                box = boxes[i]
                x0 = box[0]
                y0 = box[1]
                dx = box[2]
                dy = box[3]
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
                if len(text) > 1 and vratio > 1.3:
                    with open(verttxt, 'a', encoding="utf-8") as fo:
                        fo.write("{}/vertical/{}\t{}\n".format(mode,file_jpg,text))
                    im3.save(vertfile)                  
                else:              
                    with open(txtfile, 'a', encoding="utf-8") as fo:
                        fo.write("{}/{}\t{}\n".format(mode,path_jpg,text))
                    im3.save(full_jpg)
            
            # ntext = len(text)
            # if ntext == 1:
            #     im3.save(outimpath + file_jpg)
            # elif vratio < 1.5:
            #     im3.save(outimpath + file_jpg)
            #     if vratio > 1 and len(text)==2:
            #         print(file_jpg+ ": " + text)
            # else:
            #     im4 = im3.rotate(90,expand=1)
            #     im4.save(outimpath + file_jpg)              
            # print(text+ " " + str((x0,y0, x1,y1)))                
            # print(imfile)

def text_subset(): # 
    Path(outimpath).mkdir(exist_ok=True)    
    outpath = outimpath + category
    Path(outpath).mkdir(exist_ok=True)
    Path(outimpath+'vertical').mkdir(exist_ok=True)
    txtfile = datapath + mode + '.txt'

    dir = sorted(os.listdir(imgfolder))
    prevtext = ""
    for i, item in enumerate(dir):
        jsonfile = labfolder + os.path.splitext(item)[0] + ".json"
        imfile = imgfolder + item

        if i%5000 == 1:
            print(item)

        if Path(jsonfile).exists():           
            texts, boxes, text1 = read_label(jsonfile, prevtext)
            # print(item, texts)
            # print(boxes)         

            full_jpg = outimpath + category + "/" + os.path.splitext(item)[0] + "_0.jpg" 
            if Path(full_jpg).exists() == False:
                cropimage_writetxt(imfile, outimpath, category, txtfile, texts, boxes)
                # print('processed')
            prevtext = text1

      
# Step 1. Check if orientation is right. Manually realign image in correct orientation.
# check_image_orientation() 

# Step 2. Prepare SimpleDataset according to label/image pairs.
# text_subset()

def CRAFT_bbox(inpath): # aihub 이미지를 CRAFT bbox로 타이트하게 만든다. 
    paths = list(Path(inpath).glob('*.jpg'))
    for imfile in sorted(paths):
        boxfile = inpath + 'CRAFT/' + imfile.stem + ".txt"

        try:
            im = Image.open(imfile)
        except IOError:
            print("IO Error", imfile)

        width, height = im.size
        # print("{} : {} x {}".format(imfile.stem, width, height))

        with open(boxfile, 'r', encoding='utf-8') as f:
            lines = [' '.join(l.strip().split()) for l in f]        

        num_box = len(lines)

        x_min = width - 1
        x_max = 0
        y_min = height - 1
        y_max = 0
        
        for i, l in enumerate(lines):
            xy = l.split(',')
            xmin = min(int(xy[0]), int(xy[6]))  
            xmax = max(int(xy[2]), int(xy[4]))
            ymin = min(int(xy[1]), int(xy[3]))
            ymax = max(int(xy[5]), int(xy[7]))
            if xmin < 0:
                xmin = 0
            if xmax > width - 1:
                xmax = width - 1
            if ymin < 0:
                ymin = 0
            if ymax > height - 1:
                ymax = height - 1

            x_min = min(x_min, xmin)
            x_max = max(x_max, xmax)
            y_min = min(y_min, ymin)
            y_max = max(y_max, ymax)
    
        crop_box = (x_min, y_min, x_max, y_max)
        # print(crop_box)
        if x_min < x_max and y_min < y_max:
            cropped_image = im.crop(crop_box)
            cropped_image_path = inpath + 'CRAFT/' + imfile.stem + '.jpg'
            cropped_image.save(cropped_image_path)
        else:
            print(imfile.stem)

def delete_resimg(inpath): # CRAFT 폴더의 _res.jpg 이미지를 다 지운다. 
    paths = Path(inpath).glob('*_res.jpg')
    for imfile in paths:
        os.remove(imfile)
# delete_resimg(mypath +'CRAFT')

def move_img(outpath):
    inpath = outpath + 'CRAFT/'
    paths = Path(inpath).glob('*.jpg')
    for imfile in paths:
        outfile = outpath + imfile.stem + '.jpg'
        # print(imfile, outfile)
        shutil.move(imfile,outfile)

def copy_img(inpath, outpath):  
    if not os.path.isdir(outpath):
        os.mkdir(outpath)  
    paths = Path(inpath).glob('*.jpg')
    for imfile in paths:
        outfile = outpath + imfile.stem + '.jpg'
        # print(imfile, outfile)
        shutil.copy(imfile,outfile)  

# copy_img('/home/jw/data/aihub/train3/가로형간판5/', '/home/jw/data/aihub/train3_/가로형간판5/')

mypath = '/home/jw/data/aihub/train3_craft/가로형간판1/'
# CRAFT_bbox(mypath) # 굳이 안 해도 될 듯...
# move_img(mypath)

