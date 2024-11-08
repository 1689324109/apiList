# coding=utf-8
# ! /usr/bin/env python# -*- coding: utf-8 -*-
import os
import re
import base64
import urllib.parse
import json
import requests
from bs4 import BeautifulSoup
import pymysql

def save_news_body(temp, file_path="Z:/win10ref/video/"):
    # 确保目标目录存在
    os.makedirs(file_path, exist_ok=True)
    # 将内容写入 TXT 文件
    with open(os.path.join(file_path, f"videourl.txt"), 'a', encoding='utf-8') as f:
        f.write(temp.replace('\r\n', os.linesep).replace('\n', os.linesep) + '\n')  # 保留原格式

def check_url(url):
    # 打开数据库连接
    db = pymysql.connect(host='us-lsj-jplx-xhfrp.xhzdim.top',
                        user='root',
                        port=63306,
                        password='123456',
                        database='api-videp')
    
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    
    # 使用 execute()  方法执行 SQL 查询 
    cursor.execute("SELECT COUNT(1) FROM video_list WHERE video_url = '"+url+"'")
    
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    
    # 关闭数据库连接
    db.close()

    return data[0]

def save_mysql(results):
    # 连接到 MySQL 数据库
    db = pymysql.connect(host='us-lsj-jplx-xhfrp.xhzdim.top',
                        user='root',
                        port=63306,
                        password='123456',
                        database='api-videp')
    
    cursor = db.cursor()
    
    try:
        # 插入数据
        for result in results:
            if(int(check_url( result['href'])) > 0):
                continue
            sql = "INSERT INTO video_list (video_name, video_url,video_original) VALUES (%s, %s, %s)"
            values = (result['title'], result['href'],result['original'])
            cursor.execute(sql, values)
        
        db.commit()  # 提交事务
        print("数据插入成功")
    except Exception as e:
        print(f"插入数据时出错: {e}")
        db.rollback()  # 回滚事务
    finally:
        cursor.close()
        db.close()

def getRes(page):
    url = 'https://jvpktkygem.top/vod/list.html?typeid=1620&page=' + page
    try:
        response = requests.get(url)
        match = re.search(r"newVuePage\('([^']*)'\)", response.text)
        content = match.group(1)

        temp = content[3:] or ""  # 等同于 substr(3)
        temp = base64.b64decode(temp).decode('utf-8')  # atob
        temp = urllib.parse.unquote(temp)  # decodeURIComponent
        temp = json.loads(temp)  # JSON.parse
        results = getHref(temp)
        # print(results)
        print('page',page,end='')
        save_mysql(results)  # 保存到 MySQL
        return temp
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")

def getHref(html_content):
    # 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
   
    # 存储结果的数组
    results = []

    # 遍历所有 li 标签
    for li in soup.find_all('li'):
        outer_a = li.find('a', class_='lazyload')
        if outer_a:  # 确保找到了外层 a 标签
            href = outer_a['href']
            title = outer_a['title']
            original = outer_a['data-original']
            results.append({'href': href, 'title': title,'original':original})

    return results  # 返回结果

if __name__ == "__main__":
    # 测试获取第一页内容 1123 1321 1561
    for i in range(1,26358):
        getRes(str(i))

