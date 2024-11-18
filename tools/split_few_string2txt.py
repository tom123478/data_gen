input_file = '/Users/weicongcong/Desktop/code/data_gen/ocrdata/texts/Company-Shorter-Form28W.txt'
output_file = '/Users/weicongcong/Desktop/code/data_gen/ocrdata/texts/Company-Shorter-Form1000.txt'

try:
    with open(input_file, "r", encoding="utf-8") as infile:
        # 读取前 100 行
        lines = [next(infile) for _ in range(1000)]

    with open(output_file, "w", encoding="utf-8") as outfile:
        # 写入到输出文件
        outfile.writelines(lines)

    print(f"前 100 行已成功保存到 {output_file}")

except FileNotFoundError:
    print(f"文件 {input_file} 未找到，请检查路径。")
except StopIteration:
    print(f"文件 {input_file} 少于 100 行，已保存实际内容到 {output_file}")

