#!/usr/bin/env python3
"""
豆瓣电影 Top 200 爬虫
爬取电影基本信息并下载封面图
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

# 目录
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'movie_images')
DATA_FILE = os.path.join(OUTPUT_DIR, 'movies_top200.json')
os.makedirs(IMAGES_DIR, exist_ok=True)

# 列表页 headers
LIST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

# 图片下载 headers
IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://movie.douban.com/',
    'Sec-Fetch-Dest': 'image',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
}

BASE_URL = 'https://movie.douban.com/top250'


def download_cover(url, filepath):
    """下载封面图"""
    try:
        resp = requests.get(url, headers=IMG_HEADERS, timeout=30)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"  下载失败: {e}")
    return False


def main():
    print("=" * 50)
    print("🎬 豆瓣电影 Top 200 爬虫")
    print("=" * 50)
    
    all_movies = []
    
    # 豆瓣 Top 250 有10页（每页25部）
    for page in range(10):
        if len(all_movies) >= 200:
            break
        
        if page < 4:
            # 前4页用top250
            url = BASE_URL if page == 0 else f"{BASE_URL}?start={page * 25}"
        else:
            # 后面的用top250?start=100 (实际上豆瓣只有250，这里用排名100-200)
            url = f"https://movie.douban.com/top250?start={page * 25}"
        
        print(f"\n📄 第 {page + 1} 页...")
        
        try:
            resp = requests.get(url, headers=LIST_HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.find_all('div', class_='item')
            
            for item in items:
                rank_elem = item.find('em')
                if not rank_elem:
                    continue
                rank = int(rank_elem.get_text())
                if rank > 200:
                    continue
                
                # 标题
                title_elem = item.find('span', class_='title')
                title = title_elem.get_text().strip() if title_elem else ''
                
                # 中文标题
                img_elem = item.find('img')
                title_cn = img_elem.get('alt', '') if img_elem else title
                
                # 封面
                cover_url = img_elem.get('src', '') if img_elem else ''
                
                # 评分
                rating_elem = item.find('span', class_='rating_num')
                rating = float(rating_elem.get_text()) if rating_elem else 0
                
                # 链接
                link_elem = item.find('a')
                movie_url = link_elem.get('href', '') if link_elem else ''
                
                # 简介
                inq_elem = item.find('span', class_='inq')
                quote = inq_elem.get_text() if inq_elem else ''
                
                # BD信息
                info_elem = item.find('div', class_='bd')
                year = ''
                genre = ''
                if info_elem:
                    info_text = info_elem.get_text(separator=' ', strip=True)
                    year_match = re.search(r'(\d{4})', info_text)
                    if year_match:
                        year = year_match.group(1)
                    genre_match = re.search(r'/\s*([\u4e00-\u9fa5]+)\s*$', info_text)
                    if genre_match:
                        genre = genre_match.group(1)
                
                movie = {
                    'rank': rank,
                    'title': title,
                    'title_cn': title_cn,
                    'rating': rating,
                    'year': year,
                    'genre': genre,
                    'url': movie_url,
                    'cover_url': cover_url,
                    'quote': quote,
                }
                
                # 下载封面（只下载前200部的）
                if cover_url and rank <= 200:
                    safe_title = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title_cn).replace(' ', '_')[:20]
                    filename = f"{rank:03d}_{safe_title}.jpg"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    
                    if download_cover(cover_url, filepath):
                        movie['local_cover'] = filename
                        print(f"  ✓ [{rank:3d}] {title_cn}")
                
                all_movies.append(movie)
            
            print(f"  当前共 {len(all_movies)} 部")
            
        except Exception as e:
            print(f"  错误: {e}")
        
        time.sleep(1.2)
    
    # 保存
    output = {
        'total': len(all_movies),
        'source': 'douban.com/top250',
        'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'movies': all_movies[:200]
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 统计
    print("\n" + "=" * 50)
    print("📊 结果")
    print("=" * 50)
    print(f"电影总数: {len(all_movies[:200])}")
    print(f"封面下载: {len([m for m in all_movies[:200] if m.get('local_cover')])}")
    print(f"\n📁 数据: {DATA_FILE}")
    print(f"📁 封面: {IMAGES_DIR}/")


if __name__ == '__main__':
    main()
