Originally from [openocr](https://github.com/YongWookHa/Open-OCR-Engine)
<br>Generate synthetic ocr data

## _aihub.py
Step 1(check_image_orientation)로 세로 이미지 돌려주고 나서는<br>
Step 2(text_subset) 실행함. path, category, mode 변경해가며 모든 폴더 프로세싱. copy_img로 원래 text_subset을 보관해놓는다. 

## _util.py
combine_txt(): train0,train1,을 train.txt, val.txt로 통합해줌

## _qa.py
CRAFT 돌린 후:
1. 텍스트의 위치에 따라 sorting 해줌.
sort_bbox(filename)
2. 텍스트만 crop해서 다른 이미지로 저장해줌
extract_bbox(filename)
extract_bbox_folder(directory)