import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urljoin
import re
import random

# 设置多个请求头
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edge/112.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edge/96.0.1054.53',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'
]

# 基础URL
base_url = 'https://www.penn.museum/'

# 物品种类文物搜索页面URL
search_url = 'https://www.penn.museum/collections/search.php'

# 搜索关键字
search_terms = ['china', 'chinese']  # 包括 'china' 和 'chinese'

def get_random_user_agent():
    return random.choice(user_agents)

def request_with_retry(url, headers, params=None, retries=3, timeout=10):
    """带重试机制的请求函数"""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()  # 如果响应码不是200，会抛出异常
            return response
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"请求失败，正在重试...({attempt + 1}/{retries}) 错误: {e}")
                time.sleep(random.uniform(2, 5))  # 随机延时 2 到 5 秒再重试
            else:
                print(f"重试次数已用完，无法请求 {url}，错误: {e}")
                raise e  # 如果已经是最后一次重试，抛出异常终止程序

def scrape_chinese_artifacts():
    artifacts = []
    seen_artifacts = set()  # 用于去重
    total_items = 0  # 用来保存文物总数

    for term in search_terms:
        page = 1  # 在每次搜索一个新关键字时，重置 page 为 1
        params = {
            'term': term,
            'submit_term': 'Submit',
            'type[]': '1',  # 类型筛选条件，1表示物品种类
            'page': 1  # 页码会动态变化
        }

        while True:
            params['page'] = page
            print(f"正在爬取关键字 '{term}' 的第 {page} 页...")

            try:
                # 随机选择 User-Agent
                headers = {
                    'User-Agent': get_random_user_agent(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                }

                response = request_with_retry(search_url, headers, params=params)

                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找文物总数
                total_text = soup.select_one('p.text-md.text-right')
                if total_text and total_items == 0:
                    # 使用正则提取"Records"前的数字部分
                    match = re.search(r'(\d{1,3}(?:,\d{3})*)\s+Records', total_text.text)
                    if match:
                        total_items = int(match.group(1).replace(',', ''))  # 获取文物总数
                        print(f"文物总数: {total_items}")

                # 查找文物列表
                items = soup.select('div.card')  # 每个文物都在一个 div.card 中

                if not items:
                    print(f"没有找到关键字 '{term}' 的文物，爬取结束。")
                    break

                # 遍历当前页的所有文物
                for item in items:
                    title_element = item.select_one('h2 a')
                    title = title_element.text.strip() if title_element else None
                    link = urljoin(base_url, title_element['href']) if title_element else None
                    object_id = item.select_one('p.text-sm').text.strip() if item.select_one('p.text-sm') else None
                    object_type = item.select('div.label p.text-sm')[1].text.strip() if len(item.select('div.label p.text-sm')) > 1 else None
                    image = urljoin(base_url, item.select_one('img')['src']) if item.select_one('img') else None

                    # 使用 object_id 或 link 来避免重复抓取
                    if object_id in seen_artifacts or link in seen_artifacts:
                        continue  # 如果已经抓取过该文物，跳过

                    # 获取详情页信息
                    detail_info = scrape_detail_page(link)

                    artifact = {
                        'object_id': object_id,
                        'title': title,
                        'link': link,
                        'image': image,
                        'object_type': object_type,
                        **detail_info
                    }

                    artifacts.append(artifact)
                    seen_artifacts.add(object_id)  # 标记该文物已经抓取
                    seen_artifacts.add(link)  # 标记该文物的链接已抓取
                    print(f"已获取: {title}")

                    # 每抓取10个文物就保存一次
                    if len(artifacts) >= 10:
                        save_to_csv(artifacts)
                        artifacts.clear()  # 清空列表，准备抓取下一批文物

                # 继续抓取下一页
                page += 1

                # 如果已抓取到所有文物，停止爬取
                if total_items and len(artifacts) >= total_items:
                    print("已抓取所有文物，爬取结束。")
                    break

            except requests.exceptions.RequestException as e:
                print(f"请求出错: {e}")
                continue
    
    # 保存剩余的文物（如果有）
    if artifacts:
        save_to_csv(artifacts)

def scrape_detail_page(url):
    detail_info = {
        'object_id': None,
        'current_location': None,
        'culture': None,
        'provenience': None,
        'creator': None,
        'date_made': None,
        'section': None,
        'materials': None,
        'technique': None,
        'description': None,
        'length': None,
        'width': None,
        'credit_line': None
    }

    if not url:
        return detail_info

    try:
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = request_with_retry(url, headers)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取详情页信息
        detail_info['object_id'] = soup.select_one('td.left:contains("Object Number") + td.center').text.strip() if soup.select_one('td.left:contains("Object Number") + td.center') else None
        detail_info['current_location'] = soup.select_one('td.left:contains("Current Location") + td.center').text.strip() if soup.select_one('td.left:contains("Current Location") + td.center') else None
        detail_info['culture'] = soup.select_one('td.left:contains("Culture") + td.center').text.strip() if soup.select_one('td.left:contains("Culture") + td.center') else None
        detail_info['provenience'] = soup.select_one('td.left:contains("Provenience") + td.center').text.strip() if soup.select_one('td.left:contains("Provenience") + td.center') else None
        detail_info['creator'] = soup.select_one('td.left:contains("Creator") + td.center').text.strip() if soup.select_one('td.left:contains("Creator") + td.center') else None
        detail_info['date_made'] = soup.select_one('td.left:contains("Date Made") + td.center').text.strip() if soup.select_one('td.left:contains("Date Made") + td.center') else None
        detail_info['section'] = soup.select_one('td.left:contains("Section") + td.center').text.strip() if soup.select_one('td.left:contains("Section") + td.center') else None
        detail_info['materials'] = soup.select_one('td.left:contains("Materials") + td.center').text.strip() if soup.select_one('td.left:contains("Materials") + td.center') else None
        detail_info['technique'] = soup.select_one('td.left:contains("Technique") + td.center').text.strip() if soup.select_one('td.left:contains("Technique") + td.center') else None
        detail_info['description'] = soup.select_one('td.left:contains("Description") + td.center p').text.strip() if soup.select_one('td.left:contains("Description") + td.center p') else None
        detail_info['length'] = soup.select_one('td.left:contains("Length") + td.center').text.strip() if soup.select_one('td.left:contains("Length") + td.center') else None
        detail_info['width'] = soup.select_one('td.left:contains("Width") + td.center').text.strip() if soup.select_one('td.left:contains("Width") + td.center') else None
        detail_info['credit_line'] = soup.select_one('td.left:contains("Credit Line") + td.center a').text.strip() if soup.select_one('td.left:contains("Credit Line") + td.center a') else None

    except Exception as e:
        print(f"获取详情页 {url} 时出错: {e}")

    return detail_info

def save_to_csv(artifacts, filename='penn_museum_chinese_artifacts.csv'):
    if not artifacts:
        print("没有数据可保存")
        return
        
    keys = artifacts[0].keys()

    with open(filename, 'a', newline='', encoding='utf-8') as f:  # 这里使用 'a' 模式进行追加
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader() if f.tell() == 0 else None  # 如果文件为空，则写入标题
        writer.writerows(artifacts)
        
    print(f"数据已保存到 {filename}")

if __name__ == '__main__':
    scrape_chinese_artifacts()
