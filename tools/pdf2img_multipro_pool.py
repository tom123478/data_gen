import os
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pdf2image import convert_from_path

def read_dir_get_files(path):
    return [f for f in os.listdir(path) if f.lower().endswith('.pdf')]

def pdf_to_images(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    try:
        # 如果需要指定poppler路径，请加入：poppler_path='你的poppler路径'
        pages = convert_from_path(pdf_path, 300)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]  # 获取 PDF 文件名（无扩展名）
        for i, page in enumerate(pages):
            image_path = os.path.join(output_folder, f"{base_name}_page_{i + 1}.jpg")
            page.save(image_path, 'JPEG')
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

def single_thread(pdf_files, output_folder):
    for pdf_file in tqdm(pdf_files, desc='convert pdf 2 img ing'):
        pdf_to_images(pdf_file, output_folder)

def thread_pool(pdf_files, out_folder, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 先创建任务
        futures = [executor.submit(pdf_to_images, pdf_file, out_folder) for pdf_file in pdf_files]
        # 使用tqdm在主线程中更新进度条
        with tqdm(total=len(pdf_files), desc="Processing PDFs", ncols=80) as pbar:
            for future in as_completed(futures):
                # 等待任务完成，如果有异常会在此抛出
                future.result()
                pbar.update(1)

def multi_process_pool(pdf_files, out_folder, max_workers=4):
    # 多进程池中同样的逻辑，只是换成ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(pdf_to_images, pdf_file, out_folder) for pdf_file in pdf_files]
        with tqdm(total=len(pdf_files), desc="Processing PDFs", ncols=80) as pbar:
            for future in as_completed(futures):
                future.result()
                pbar.update(1)

if __name__ == '__main__':
    pdf_path = '/Users/weicongcong/Desktop/code/cyclegan/kaoyan'
    output_folder = '/Users/weicongcong/Desktop/code/cyclegan/dianzi'
    pdf_files = [os.path.join(pdf_path, f) for f in read_dir_get_files(pdf_path)]

    start = time.time()
    print("Starting thread pool conversion...")
    # thread_pool(pdf_files, output_folder, max_workers=4)  # 使用线程池
    # single_thread(pdf_files, output_folder)  # 单线程处理
    multi_process_pool(pdf_files, output_folder, max_workers=4) # 使用多进程池
    end = time.time()
    print(f"Thread pool conversion completed in {end - start:.2f} seconds")
