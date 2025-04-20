import pandas as pd

# 读取原始数据
file_path = "D:/sp/2china_met_museum_data.csv"
df = pd.read_csv(file_path)

# 复制数据（防止修改原始 DataFrame）
df_cleaned = df.copy()

# 1. 替代 inplace，推荐使用赋值方式
df_cleaned['Title'] = df_cleaned['Title'].fillna('unknown')
df_cleaned['Period'] = df_cleaned['Period'].fillna('unknown')
df_cleaned['Medium'] = df_cleaned['Medium'].fillna('unknown')
df_cleaned['Image'] = df_cleaned['Image'].fillna('no_image')
df_cleaned['Image Download Link'] = df_cleaned['Image Download Link'].fillna('unknown')
df_cleaned['Artist'] = df_cleaned['Artist'].fillna('unknown')

# 2. 字符串标准化处理
for col in ['Title', 'Period', 'Medium', 'Artist']:
    df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.lower()

# 3. 替换变体（去除奇怪的 unknown 形式）
df_cleaned = df_cleaned.replace({'unknown ': 'unknown', 'Unknown': 'unknown'})

# 4. 删除重复行
df_cleaned = df_cleaned.drop_duplicates()

# 5. 可选：仅保留有图像的记录
df_with_images = df_cleaned[df_cleaned['Image'] != 'no_image']
########################
df_cleaned['Object ID'] = range(1, len(df_cleaned) + 1)
# 6. 保存结果（可选）
df_cleaned.to_csv("cleaned_data.csv", index=False, encoding='utf-8')
df_with_images.to_csv("cleaned_data_with_images.csv", index=False)

print("✅ 数据清洗完成，已保存为 cleaned_data.csv 和 cleaned_data_with_images.csv")
