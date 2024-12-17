from pdf2image import convert_from_path
import os
from tqdm import tqdm
import time

def read_dir_get_files(path):
    return [f for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')]


def pdf_to_images(pdf_path, output_folder, start_num):
    """
    Convert each page of a PDF to an image and save it.

    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str): Folder to save the output images.
        start_num (int): Starting index for naming output images.
    Returns:
        int: The updated start_num after processing this PDF.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # Convert PDF pages to images
        pages = convert_from_path(pdf_path, 300)  # 300 DPI for good quality

        for i, page in enumerate(pages):
            image_path = os.path.join(output_folder, f"page_{start_num + i + 1}.jpg")
            page.save(image_path, 'JPEG')
            print(f"Saved: {image_path}")

        # Update and return the next start_num
        return start_num + len(pages)

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return start_num  # If error, return unchanged start_num


if __name__ == "__main__":
    pdf_path = '/Users/weicongcong/Desktop/code/cyclegan/kaoyan'
    output_folder = '/Users/weicongcong/Desktop/code/cyclegan/dianzi'
    num = 0  # Initial image index

    start_time = time.time()
    # Filter PDF files only
    pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')]

    for pdf_file in tqdm(pdf_files, desc="Converting PDFs"):
        num = pdf_to_images(os.path.join(pdf_path, pdf_file), output_folder, num)
    
    end_time = time.time()
    elapsed = end_time-start_time

    print("All pages have been converted to images.")
    print("time is {elapsed:.6f}")

