# coding=utf-8
# ! /usr/bin/env python# -*- coding: utf-8 -*-
import http
import os
import re
import ssl
from asyncio import sleep
import pymysql

import requests
from bs4 import BeautifulSoup
import base64
import urllib.parse
import json


def save_news_body(temp, file_path="Z:/win10ref/video/"):
    temp = temp[3:] or ""  # 等同于 substr(3)
    temp = base64.b64decode(temp).decode('utf-8')  # atob
    temp = urllib.parse.unquote(temp)  # decodeURIComponent
    temp = json.loads(temp)  # JSON.parse

    # 解析 HTML
    soup = BeautifulSoup(temp, 'html.parser')

    # 查找视频标签
    video_tag = soup.find('video')
    if video_tag:
        # 获取 <source> 标签的 src 属性
        source_tag = video_tag.find('source')
        title = soup.find('div', class_='player_title').text.strip()

        title_div = soup.find('div', class_='player_title')
        if title_div:
            # 提取所有文本并去掉多余空白
            title_text = ' '.join(title_div.stripped_strings)

            # 找到最后一个 » 符号并提取后面的文本
            if '»' in title_text:
                after_arrow = title_text.split('»')[-1].strip()  # 取最后一部分
                title = after_arrow
            else:
                print("标题中未找到 '»' 符号。")

        if source_tag and 'src' in source_tag.attrs:
            video_src = source_tag['src']
            # 确保目标目录存在
            os.makedirs(file_path, exist_ok=True)
            # 将内容写入 TXT 文件
            with open(os.path.join(file_path, f"videoList.txt"), 'a', encoding='utf-8') as f:
                f.write(title + ':' + video_src.replace('\r\n', os.linesep).replace('\n', os.linesep) + '\n')  # 保留原格式
            print('title'+title+' video:'+ video_src)
        else:
            print("未找到视频源链接。")

    return temp

def update_mysql(id,url):
        # 打开数据库连接
    db = pymysql.connect(host='192.168.17.220',
                        user='root',
                        password='123456',
                        database='api-videp')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 更新语句
    update_query = """
    UPDATE video_list
    SET video_msbu = %s
    WHERE id = %s
    """


    try:
        # 执行更新操作
        cursor.execute(update_query, (url, id))
        db.commit()  # 提交更改
        print("更新成功")
    except Exception as e:
        db.rollback()  # 如果发生错误，则回滚
        print(f"更新失败: {e}")

    # 关闭数据库连接
    db.close()

def save_mysql(id,temp):
    temp = temp[3:] or ""  # 等同于 substr(3)
    temp = base64.b64decode(temp).decode('utf-8')  # atob
    temp = urllib.parse.unquote(temp)  # decodeURIComponent
    temp = json.loads(temp)  # JSON.parse

    # 解析 HTML
    soup = BeautifulSoup(temp, 'html.parser')

    # 查找视频标签
    video_tag = soup.find('video')
    if video_tag:
        # 获取 <source> 标签的 src 属性
        source_tag = video_tag.find('source')
        video_src = source_tag['src']

        if source_tag and 'src' in source_tag.attrs:
          update_mysql(id,video_src)
        else:
            print("未找到视频源链接。")

    return temp

def getbase64(url):
    content = ''
    for i in range(1, 10):
        try:
            url = 'https://jvpktkygem.top' + url
            print(url +"\n")
            response = requests.get(url)
            match = re.search(r"newVuePage\('([^']*)'\)", response.text)
            if match:
                content = match.group(1)
            break  # 成功后退出循环
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}，尝试第 {i + 1} 次重试...")
            sleep(1)
    return content


def getRes():
    url = 'https://jvpktkygem.top/vod/detail.html?id=1751692'
    try:
        response = requests.get(url)
        match = re.search(r"newVuePage\('([^']*)'\)", response.text)
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")

def from_mysql():

    # 打开数据库连接
    db = pymysql.connect(host='192.168.17.220',
                        user='root',
                        password='123456',
                        database='api-videp')

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    # 使用 execute() 方法执行 SQL 查询 
    cursor.execute("SELECT id,video_name,video_url,video_original,video_msbu FROM video_list WHERE video_msbu is NULL")

    # 使用 fetchall() 方法获取所有数据
    data = cursor.fetchall()

    # 循环输出每条数据
    for row in data:
        temp =  getbase64(row[2])
        save_mysql(row[0],temp)
        # print(temp) 
        # print("ID: %s, Video Name: %s, Video URL: %s, Video Original: %s, Video MSBU: %s" % row)
    db.close()

if __name__ == "__main__":
    while True :
        from_mysql()
        sleep(1)