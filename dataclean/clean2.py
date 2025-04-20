import pandas as pd

# 读取文件（注意根据实际编码选择）
df = pd.read_csv("D:/sp/10_clevelandart_museum_data.csv", encoding='gbk')  # 替换为你的实际文件名

# 保留指定字段
df = df[['id', 'tombstone', 'title', 'creation_date', 'collection',
         'provenance', 'url', 'image_web']]

# 1. 替换空值：通用字段 → "unknown"，image_web → "no_image"
df.fillna(value={
    'tombstone': 'unknown',
    'title': 'unknown',
    'creation_date': 'unknown',
    'collection': 'unknown',
    'provenance': 'unknown',
    'url': 'unknown',
    'image_web': 'no_image'
}, inplace=True)

# 2. 字符串标准化：统一小写 & 去除前后空格
for col in ['tombstone', 'title', 'creation_date', 'collection',
            'provenance', 'url', 'image_web']:
    df[col] = df[col].astype(str).str.strip().str.lower()

# 3. 异常值清理（如 "Unknown " → "unknown"）：已在上一步完成

# 4. 删除完全重复的行
df.drop_duplicates(inplace=True)
#############
df.reset_index(drop=True, inplace=True)
df['id'] = df.index + 1
# 保存清洗后的结果
df.to_csv('cleaned_data2.csv', index=False, encoding='utf-8-sig')
