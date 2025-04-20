import requests
import pandas as pd
import time

def get_object_details(object_id):
    """获取单个文物详细信息，增加超时和异常处理"""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # 获取详细信息，包括标题、年代、类型、图片、入藏编号等
            title = data.get('title', 'Unknown')
            period = data.get('objectDate', 'Unknown')  # 使用objectDate字段作为时代
            medium = data.get('medium', 'Unknown')  # 使用medium字段作为替代描述
            primary_image = data.get('primaryImage', None)  # 确保图片字段为空时设置为None
            
            # 如果图片为空，则设置为'Unknown'
            primary_image_url = 'Unknown' if not primary_image else primary_image

            object_url = data.get('objectURL', 'Unknown')
            artist = data.get('artistDisplayName', 'Unknown')  # 使用默认值'Unknown'如果为空

            # 如果没有原图链接，则标记为'Unknown'
            if not primary_image_url:
                primary_image_url = 'Unknown'

            # 如果artist为空，则设置为'Unknown'
            if not artist:
                artist = 'Unknown'

            return {
                'Object ID': object_id,  # 文物ID
                'Title': title,
                'Period': period,  # 时代字段，可能是'objectDate'
                'Medium': medium,  # 替代的描述字段
                'Image': primary_image,
                'Image Download Link': primary_image_url,
                'Object URL': object_url,
                'Artist': artist
            }
        else:
            print(f"请求失败: {object_id}, 状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常: {object_id}, 错误: {str(e)}")
        return None


def get_china_object_ids():
    base_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    keywords = ["China", "Chinese"]  
    all_ids = set()  
    
    for keyword in keywords:
        params = {
            "q": keyword,
        }
        while True:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                ids = data.get("objectIDs", [])
                all_ids.update(ids)
                print(f"关键词 '{keyword}' 找到 {len(ids)} 个结果")
                
                # 如果返回的结果有分页信息，获取下一页的数据
                next_page = data.get('next', None)
                if next_page:
                    params['page'] = next_page  # 更新分页参数
                else:
                    break  # 如果没有下一页，退出循环
            else:
                print(f"关键词 '{keyword}' 请求失败: 状态码 {response.status_code}")
                break
    
    print(f"总计去重后的文物ID数量: {len(all_ids)}")
    return sorted(list(all_ids))  # 对文物ID进行排序，确保输出从小到大


def fetch_and_save_china_data():
    """主函数：获取数据并保存为CSV"""
    object_ids = get_china_object_ids()
    if not object_ids:
        print("未找到任何中国文物ID")
        return
    
    seen_accession_numbers = set()  # 用来存储已处理的入藏编号
    data = []
    header_written = False  # 用来标记是否已经写入过表头
    
    for idx, object_id in enumerate(object_ids, 1):
        if idx % 5 == 0:  # 每5次请求暂停1秒，避免被封IP
            time.sleep(1)
        
        print(f"正在处理第 {idx}/{len(object_ids)} 个文物: ID {object_id}")
        details = get_object_details(object_id)
        
        if details:
            data.append(details)

            # 每10条数据保存一次
            if len(data) >= 10:
                df = pd.DataFrame(data)
                df.to_csv("china_met_museum_data.csv", index=False, encoding="utf-8", mode='a', header=not header_written)
                header_written = True  
                print(f"已保存 {len(data)} 条数据到 CSV 文件！")
                data = []  
                

    # 保存剩余数据
    if data:
        df = pd.DataFrame(data)
        df.to_csv("china_met_museum_data.csv", index=False, encoding="utf-8", mode='a', header=not header_written)
        print(f"成功保存 {len(data)} 条数据到 CSV 文件！")

# 运行主程序
fetch_and_save_china_data()
