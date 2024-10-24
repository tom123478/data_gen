from PIL import Image
import os

###
# CRAFT의 output으로 나온 bbox를 sort해서 글을 읽는 순서대로 배열함
###
def sort_bbox(boxfile):  
  folder = os.path.dirname(boxfile)
  filename, txt = os.path.splitext(os.path.basename(boxfile))
  
  boxfile2 = folder + '/' + filename + '_CRAFT' + txt     

  with open(boxfile, 'r', encoding='utf-8') as f:
    line = [' '.join(l.strip().split()) for l in f]   
  
  num_box = len(line)
  boxes = []
  lines = []
  py_ave = 0

  ## boxes contains minimum x, y coordinates of the bbox 
  for i, l in enumerate(line):
    xy = l.split(',')
    lines.append([xy[0],xy[1],xy[2],xy[3],xy[4],xy[5],xy[6],xy[7]])
    xmin = min(int(xy[0]), int(xy[6]))      
    ymin = min(int(xy[1]), int(xy[3]))
    ymax = max(int(xy[5]), int(xy[7]))
    py = ymax-ymin
    py_ave += py
    boxes.append([i, xmin, ymin])       
  # print(boxes)
    
  py_ave /= num_box
  print(py_ave)
  thresh = py_ave/2
  
  ## sorted_box contains boxes sorted by y-coordinate, then x-coordinate
  sorted_box = sorted(boxes, key=lambda pair: (pair[2], pair[1]))
  # print(sorted_box)

  ## we'll group each line based on the half of box heights as threshold
  y0 = sorted_box[0][2]
  # print(y0)
  for i in range(num_box):
    y = sorted_box[i][2]
    if( y - y0 < thresh ):
      sorted_box[i][2] = y0
    else:
       y0 = y
  # print(sorted_box)

  ## sorted_box_final is sorted based on x coordinates of each line
  sorted_box_final = sorted(sorted_box, key=lambda pair: (pair[2], pair[1]))
  # print(sorted_box_final)

  ## Now print out the sorted bbox list as new boxfile
  with open(boxfile2, 'w', encoding='utf-8') as fo:
    for i in range(num_box):
       index = sorted_box_final[i][0]
       xy = lines[index]
       fo.write("{},{},{},{},{},{},{},{}\n".format(xy[0],xy[1],xy[2],xy[3],xy[4],xy[5],xy[6],xy[7]))        

# sort_bbox('/home/jw/data/test/1/CRAFT/news.txt')

###
# 폴더에 있는 모든 bbox.txt 파일을 sort함 
###
def sort_bbox_folder(directory):
  for file in os.listdir(directory):
    if file.endswith('.txt'):
      filepath = os.path.join(directory,file)
      print(filepath)
      sort_bbox(filepath)

# sort_bbox_folder('/home/jw/data/test/1/CRAFT')
   
###
# CRAFT의 output인 bbox대로 image를 crop함
### 
def extract_bbox(imfile): # post-process CRAFT to write text bbox images
    folder = os.path.dirname(imfile)
    imname, ext = os.path.splitext(os.path.basename(imfile))
    outpath = folder + '/' + imname + '/'
    boxfile = folder + '/CRAFT/' + imname + '.txt'
    # print(ext)
    # print(boxfile)
    try:
        os.makedirs(outpath)
    except:
        print("folder already exists")   

    im = Image.open(imfile)
    with open(boxfile, 'r', encoding='utf-8') as f:
        lines = [' '.join(l.strip().split()) for l in f]        
    f.close()
    num_box = len(lines)
    for i, l in enumerate(lines):
        xy = l.split(',')
        xmin = min(int(xy[0]), int(xy[6]))  
        xmax = max(int(xy[2]), int(xy[4]))
        ymin = min(int(xy[1]), int(xy[3]))
        ymax = max(int(xy[5]), int(xy[7]))
 
        crop_box = (xmin, ymin, xmax, ymax)
        # print(crop_box)
        cropped_image = im.crop(crop_box)
        cropped_image_path = outpath + '/' + imname + '_' + str(i+1) + ext
        cropped_image.save(cropped_image_path)

# extract_bbox('/home/jw/data/test/1/report.png')

###
# 한 폴더에 대해서 모든 이미지를 CRAFT bbox대로 crop함 
### 
def extract_bbox_folder(directory):
    entries = os.listdir(directory)
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    for file in files:
        extract_bbox(directory+'/'+file)
        
# extract_bbox_folder('/home/jw/data/test/1/')


###
# PaddleOCR 결과를 읽고 포맷을 다시 한다. 
# /home/jw/data/test/2/cosmetic/box/cosmetic_001.jpg	('구달', 0.9942219257354736)
# => src  result  probability
###
def PaddleResult(infile, outfile):
  with open(infile, 'r', encoding='utf-8') as fin:
    lines = [' '.join(l.strip().split()) for l in fin] 
  
  with open(outfile, 'w', encoding='utf-8') as fo:
    for i, l in enumerate(lines):
        line = l.split(' ')
        img = line[0]
        res = line[1][2:-2]    
        prob = line[2][:-1]
        print("{}\t{}\t{}".format(img, res, prob))
        fo.write("{}\t{}\t{}\n".format(img, res, prob))

PaddleResult('/home/jw/data/test/2/cosmetic.txt','/home/jw/data/test/2/cosmetic_paddle.txt')