from PIL import Image
import os

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

def extract_bbox_folder(directory):
    entries = os.listdir(directory)
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
    for file in files:
        extract_bbox(directory+'/'+file)
        
extract_bbox_folder('/home/jw/data/test/1/')
