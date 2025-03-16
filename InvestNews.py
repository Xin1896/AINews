import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template
from datetime import datetime
import os

app = Flask(__name__)

def get_investment_news():
    """
    获取最新的投资信息
    这里使用了几个知名财经网站作为数据源
    """
    news_list = []
    
    # 从新浪财经获取信息
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://finance.sina.com.cn/stock/', headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找新闻标题元素
        news_elements = soup.select('.news-list li a')
        for element in news_elements[:2]:  # 获取前两条
            title = element.text.strip()
            link = element['href']
            news_list.append({
                'title': title,
                'source': '新浪财经',
                'link': link,
                'time': datetime.now().strftime('%Y-%m-%d')
            })
    except Exception as e:
        print(f"从新浪财经获取数据失败: {e}")
    
    # 从东方财富网获取信息
    try:
        response = requests.get('https://www.eastmoney.com/', headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_elements = soup.select('.news-wrap .news-item a')
        for element in news_elements[:2]:  # 获取前两条
            title = element.text.strip()
            link = element['href']
            if title and not any(news['title'] == title for news in news_list):
                news_list.append({
                    'title': title,
                    'source': '东方财富',
                    'link': link,
                    'time': datetime.now().strftime('%Y-%m-%d')
                })
                if len(news_list) >= 3:
                    break
    except Exception as e:
        print(f"从东方财富获取数据失败: {e}")
    
    # 如果还不够3条，从第三个源获取
    if len(news_list) < 3:
        try:
            response = requests.get('https://www.jrj.com.cn/', headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_elements = soup.select('.news-wrap .news-item')
            for element in news_elements:
                title_element = element.select_one('a')
                if title_element:
                    title = title_element.text.strip()
                    link = title_element['href']
                    if title and not any(news['title'] == title for news in news_list):
                        news_list.append({
                            'title': title,
                            'source': '金融界',
                            'link': link,
                            'time': datetime.now().strftime('%Y-%m-%d')
                        })
                        if len(news_list) >= 3:
                            break
        except Exception as e:
            print(f"从金融界获取数据失败: {e}")
    
    return news_list[:3]  # 返回前3条新闻

@app.route('/')
def index():
    news = get_investment_news()
    return render_template('index.html', news=news, update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# 创建模板目录和文件
def create_template():
    if not os.path.exists('templates'):
        os.mkdir('templates')
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>今日投资信息</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .news-item {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .news-title {
            font-size: 18px;
            margin-bottom: 5px;
        }
        .news-title a {
            color: #0066cc;
            text-decoration: none;
        }
        .news-title a:hover {
            text-decoration: underline;
        }
        .news-source {
            color: #666;
            font-size: 14px;
        }
        .news-time {
            color: #999;
            font-size: 12px;
        }
        .update-time {
            text-align: center;
            font-size: 12px;
            color: #999;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>今日投资最新信息</h1>
    
    {% if news %}
        {% for item in news %}
        <div class="news-item">
            <div class="news-title">
                <a href="{{ item.link }}" target="_blank">{{ item.title }}</a>
            </div>
            <div class="news-source">来源: {{ item.source }}</div>
            <div class="news-time">日期: {{ item.time }}</div>
        </div>
        {% endfor %}
    {% else %}
        <p>暂无最新投资信息</p>
    {% endif %}
    
    <div class="update-time">最后更新时间: {{ update_time }}</div>
</body>
</html>
        ''')

if __name__ == '__main__':
    create_template()
    print("启动服务器，请访问 http://127.0.0.1:5000/")
    app.run(debug=True)