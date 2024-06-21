originally from [openocr](https://github.com/YongWookHa/Open-OCR-Engine)
generate synthetic ocr data

## _aihub.py
Step 1(check_image_orientation)로 세로 이미지 돌려주고 나서는
Step 2(text_subset) 실행함. path, category, mode 변경해가며 모든 폴더 프로세싱. copy_img로 원래 text_subset을 보관해놓는다. 

## _util.py
combine_txt(): train0,train1,을 train.txt, val.txt로 통합해줌