import sys
import json
import requests
from bs4 import BeautifulSoup
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import colorsys
import qrcode
import base64
from io import BytesIO
import time

# 设置代理
PROXY = "127.0.0.1:7890"
proxies = {
    "http": f"http://{PROXY}",
    "https": f"http://{PROXY}"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

ITEMS_FILE = os.path.join(os.path.dirname(__file__), 'items_data.json')

def load_items():
    if os.path.exists(ITEMS_FILE):
        try:
            with open(ITEMS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("JSONDecodeError: 无法解析商品数据文件")
            return []
    return []

def save_items(items):
    with open(ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=4)

def get_latest_item():
    URL = "https://booth.pm/zh-cn/items?in_stock=true&sort=new&tags%5B%5D=VRChat"
    response = requests.get(URL, headers=HEADERS, proxies=proxies)
    soup = BeautifulSoup(response.content, 'html.parser')
    item = soup.find('li', class_='item-card')
    
    if item:
        item_id = item['data-product-id']
        return get_item_by_id(item_id)
    return None

def get_item_by_id(item_id):
    item_data_url = f"https://booth.pm/zh-cn/items/{item_id}.json"
    response = requests.get(item_data_url, headers=HEADERS, proxies=proxies)
    if response.status_code != 200:
        print(f"无法获取商品数据，状态码：{response.status_code}")
        return None

    try:
        item_data = response.json()
    except ValueError:
        print("无法解析商品JSON数据")
        return None

    # 获取商品的详细信息
    title = item_data.get('name', '无标题')
    price = item_data.get('price', '无价格')
    author = item_data.get('shop', {}).get('name', '无作者')
    author_thumbnail_url = item_data.get('shop', {}).get('thumbnail_url', '')
    description = item_data.get('description', '无详细描述')
    link = item_data.get('url', '')
    category = item_data.get('category', {}).get('name', '无分类')
    parent_category = item_data.get('category', {}).get('parent', {}).get('name', '无父分类')
    tags = item_data.get('tags', [])
    is_adult = item_data.get('is_adult', False)

    # 获取喜欢数
    wish_list_link = f"https://accounts.booth.pm/wish_lists.json?item_ids%5B%5D={item_id}"
    wish_response = requests.get(wish_list_link, headers=HEADERS, proxies=proxies)
    if wish_response.status_code != 200:
        print(f"无法获取喜欢数数据，状态码：{wish_response.status_code}")
        likes = 0
    else:
        try:
            wish_data = wish_response.json()
            likes = wish_data.get('wishlists_counts', {}).get(str(item_id), 0)
        except ValueError:
            print("无法解析喜欢数JSON数据")
            likes = 0

    # 获取图片URL
    image_url = item_data.get('images', [{}])[0].get('original', '无图片')

    return {
        'id': item_id,
        'title': title,
        'price': price,
        'image_url': image_url,
        'link': link,
        'category': category,
        'parent_category': parent_category,
        'author': author,
        'author_thumbnail_url': author_thumbnail_url,
        'description': description,
        'likes': likes,
        'tags': tags,
        'is_adult': is_adult
    }

def get_dominant_color(image_url):
    response = requests.get(image_url, proxies=proxies)
    img = Image.open(BytesIO(response.content))
    img = img.convert('RGB')
    img = img.resize((1, 1))
    dominant_color = img.getpixel((0, 0))
    
    # 将RGB转换为HSL
    h, l, s = colorsys.rgb_to_hls(dominant_color[0]/255, dominant_color[1]/255, dominant_color[2]/255)
    
    # 调整亮度和饱和度
    l = min(max(l, 0.3), 0.7)  # 确保亮度在30%到70%之间
    s = min(s * 1.2, 1.0)  # 增加饱和度，但不超过100%
    
    # 转换回RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_preview_image(item):
    # 检查是否为成人内容或包含 "R18" 标签
    if item['is_adult'] or any(tag['name'] == 'R18' for tag in item['tags']):
        image_url = "https://s21.ax1x.com/2024/08/29/pAA3n6e.png"
    else:
        image_url = item['image_url']
        
    dominant_color = get_dominant_color(image_url)
    qr_code_base64 = generate_qr_code(item['link'])
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Noto Sans SC', Arial, sans-serif;
                background: #f0f0f0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .container {{
                width: 600px;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                position: relative;
            }}
            .header {{
                background: linear-gradient(135deg, {dominant_color}, #ffffff);
                color: #333;
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
                text-align: left;
                position: relative;
                overflow: hidden;
            }}
            .header::after {{
                content: "VRChat";
                position: absolute;
                right: -20px;
                top: 50%;
                transform: translateY(-50%) rotate(-90deg);
                font-size: 72px;
                opacity: 0.1;
                font-weight: 900;
            }}
            .content {{
                display: flex;
                padding: 15px;
                flex-wrap: wrap;
            }}
            .image {{
                width: 200px;
                height: 200px;
                background-image: url('{image_url}');
                background-size: cover;
                background-position: center;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                flex-shrink: 0;
            }}
            .info {{
                margin-left: 20px;
                flex: 1;
                min-width: 280px;
                max-width: 320px;
                position: relative;
            }}
            h2 {{
                margin: 0;
                font-size: 20px;
                color: #333;
                line-height: 1.4;
            }}
            p {{
                margin: 8px 0;
                font-size: 16px;
                color: #666;
            }}
            .price-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: -30
            }}
            .price {{
                font-size: 30px;
                font-weight: bold;
                color: #FF6B6B;
            }}
            .category {{
                background: #f0f0f0;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 14px;
                display: inline-block;
                margin-bottom: -30px;
            }}
            .likes {{
                display: flex;
                align-items: center;
                color: #FF6B6B;
                font-weight: bold;
                margin-top: -35px;
            }}
            .likes::before {{
                content: "♥";
                margin-right: 5px;
            }}
            .description {{
                padding: 20px;
                font-size: 14px;
                color: #333;
                max-height: 80px;
                overflow-y: hidden;
                line-height: 1.6;
                margin-top: 0px;
                flex-grow: 1;
            }}
            .footer {{
                background: #333;
                color: white;
                text-align: center;
                padding: 10px;
                font-size: 14px;
                position: relative;
            }}
            .footer::before {{
                content: "BOOTH";
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                font-weight: bold;
                font-size: 18px;
            }}
            .label {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255,255,255,0.9);
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }}
            .qr-code {{
                width: 120px;
                height: 120px;
                background-image: url(data:image/png;base64,{qr_code_base64});
                background-size: cover;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .logo {{
                width: 50px;
                height: auto;
                vertical-align: middle;
                margin-left: 5px;
                position: relative;
                top: 3px;
            }}
            .author {{
                display: flex;
                align-items: center;
                margin-top: 40px;
            }}
            .author img {{
                width: 32px;
                height: 32px;
                border-radius: 50%;
                margin-right: 10px;
            }}
            .author-name {{
                font-size: 14px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                VRChat 商品
                <div class="label">New!</div>
            </div>
            <div class="content">
                <div class="image"></div>
                <div class="info">
                    <h2>{item['title'][:50]}{'...' if len(item['title']) > 50 else ''}</h2>
                    <div class="category">{item['category']} -> {item['parent_category']}</div>
                    <div class="author">
                        <img src="{item['author_thumbnail_url']}" alt="Author Thumbnail">
                        <span class="author-name">{item['author']}</span>
                        </div>
                    <div class="price-container">
                        <p class="price">{item['price']}</p>
                        <div class="qr-code"></div>
                    </div>
                    <div class="likes">{item['likes']} 人喜欢</div>
                </div>
                <div class="description">{item['description'][:150]}{'...' if len(item['description']) > 150 else ''}</div>
            </div>
            <div class="footer">
                由XXX生成 | 来自
                <img src="https://s21.ax1x.com/2024/09/01/pAEbYs1.png" class="logo" alt="Logo">
            </div>
        </div>
    </body>
    </html>
    """

    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'--proxy-server={PROXY}')

    # 初始化WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 创建一个临时HTML文件
        with open("temp.html", "w", encoding="utf-8") as f:
            f.write(html)

        # 打开HTML文件
        driver.get("file://" + os.path.abspath("temp.html"))

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "container"))
        )

        # 暂停以确保图像加载
        time.sleep(2)

        # 获取容器元素
        container = driver.find_element(By.CLASS_NAME, "container")

        # 截图
        if not os.path.exists('data'):
            os.makedirs('data')
        container.screenshot(f"data/{item['id']}.png")

    finally:
        # 关闭浏览器
        driver.quit()

    # 删除临时HTML文件
    os.remove("temp.html")


def main():
    if len(sys.argv) < 2:
        print("用法: python booth_image.py [generate|fetch] ...")
        return

    mode = sys.argv[1]
    
    if mode == "fetch":
        latest_item = get_latest_item()
        if latest_item:
            old_items = load_items()
            if not old_items or old_items[0]['id'] != latest_item['id']:
                save_items([latest_item] + old_items)
                print("最新商品信息已更新。")
            else:
                print("没有新商品。")
        else:
            print("未能获取最新商品信息。")
    
    elif mode == "generate":
        if len(sys.argv) < 3:
            print("用法: python booth_image.py generate <item_id>")
            return

        item_id = sys.argv[2]
        item = get_item_by_id(item_id)
        
        if item:
            create_preview_image(item)
            print(f"商品图片已生成：data/{item_id}.png")
        else:
            print("未找到指定 ID 的商品。")
    else:
        print("无效的模式。请使用 'fetch' 或 'generate'。")

if __name__ == "__main__":
    main()
