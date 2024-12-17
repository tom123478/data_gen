import threading
from pdf2image import convert_from_path
import os
from tqdm import tqdm
import time


def read_dir_get_files(path):
    return [f for f in os.listdir(path) if f.lower().endswith('.pdf')]


def pdf_to_images(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        pages = convert_from_path(pdf_path, 300)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]  # 获取 PDF 文件名（无扩展名）

        for i, page in enumerate(pages):
            # 给图片文件名前加上 PDF 文件名作为前缀，避免重复
            image_path = os.path.join(output_folder, f"{base_name}_page_{i + 1}.jpg")
            page.save(image_path, 'JPEG')
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")



def single_thread(pdf_files, output_folder):
    for pdf_file in tqdm(pdf_files, desc='convert pdf 2 img ing'):
        pdf_to_images(pdf_file, output_folder)


def multi_thread(pdf_files, out_folder):
    threads = []
    progress_bar = tqdm(total=len(pdf_files), desc="Processing PDFs", ncols=80)

    def worker(pdf_file):
        pdf_to_images(pdf_file, out_folder)
        progress_bar.update(1)  # 每完成一个任务，更新进度条

    for pdf_file in pdf_files:
        thread = threading.Thread(target=worker, args=(pdf_file,))
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    progress_bar.close()


if __name__ == '__main__':
    pdf_path = '/Users/weicongcong/Desktop/code/cyclegan/kaoyan'
    output_folder = '/Users/weicongcong/Desktop/code/cyclegan/ceshi1'
    pdf_files = [os.path.join(pdf_path, f) for f in read_dir_get_files(pdf_path)]

    start = time.time()
    print("Starting multi-threaded conversion...")
    # multi_thread(pdf_files, output_folder)
    single_thread(pdf_files, output_folder)
    end = time.time()
    print(f"Multi-threaded conversion completed in {end - start:.2f} seconds")
