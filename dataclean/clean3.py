import pandas as pd

# 读取原始 CSV 文件
df = pd.read_csv('D:/pycharm/pythonProject/sp/16penn_museum_chinese_artifacts.csv')

# 要保留的字段
fields = ['object_id', 'provenience', 'creator', 'date_made', 'materials', 'description', 'length', 'width']

# 只保留这些字段，没有的就填 unknown
for field in fields:
    if field not in df.columns:
        df[field] = 'unknown'

# 填充空值为 "unknown"
df = df[fields].fillna('unknown')

# object_id 从 1 开始重新编号
df['object_id'] = range(1, len(df) + 1)

# 保存新 CSV 文件
df.to_csv('filtered_data.csv', index=False)

print("处理完成，新文件已保存为 filtered_data.csv")
