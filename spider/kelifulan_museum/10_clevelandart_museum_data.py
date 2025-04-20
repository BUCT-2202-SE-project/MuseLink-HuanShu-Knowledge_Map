import csv

# 输入文件名
input_file = 'data/data2.csv'
# 输出文件名
output_file = 'data/china.csv'
# 筛选的关键字
keyword = 'china'

# 打开输入文件并读取内容
with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)  # 使用 DictReader 以便通过字段名访问数据
    # 获取所有字段名，用于后续写入输出文件
    fieldnames = reader.fieldnames

    # 打开输出文件并写入筛选后的记录
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()  # 写入表头

        # 遍历输入文件的每一行
        for row in reader:
            # 检查指定字段是否包含关键字
            if keyword.lower() in row['culture'].lower():  # 假设字段名为 'Country'
                writer.writerow(row)  # 将符合条件的行写入输出文件

print(f"筛选完成，结果已保存到 {output_file}")