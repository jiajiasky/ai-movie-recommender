#!/usr/bin/env python3
"""
电影相似度计算与推荐生成
基于：类型、导演、演员、MBTI群体、人生阶段、评分
"""

import json
import os
from collections import defaultdict

# 加载电影数据
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def load_movies():
    """加载电影数据"""
    # 优先使用 movies_top200.json（数据更全）
    for filename in ['movies_top200.json', 'movies_top50.json', 'movie_database.json']:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            print(f"📂 加载数据: {filename}")
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'movies' in data:
                    return data['movies']
                elif isinstance(data, list):
                    return data
    raise FileNotFoundError("未找到电影数据文件")


def normalize_genre(genre_str):
    """标准化类型标签"""
    if not genre_str:
        return set()
    # 拆分 "/" 分割的类型
    genres = set()
    for g in genre_str.replace('/', ' ').replace('，', ' ').split():
        g = g.strip()
        if g:
            genres.add(g)
    return genres


def parse_actors(actors):
    """解析演员列表"""
    if isinstance(actors, list):
        return set(actors)
    if isinstance(actors, str):
        # 尝试拆分
        actors = [a.strip() for a in actors.replace('、', ',').replace('，', ',').split(',')]
        return set(a for a in actors if a)
    return set()


def parse_mbti(mbti_groups):
    """解析MBTI群体"""
    if isinstance(mbti_groups, list):
        return set(mbti_groups)
    if isinstance(mbti_groups, str):
        return set(g.strip() for g in mbti_groups.replace(' ', '').split('/') if g.strip())
    return set()


def parse_life_stage(life_stages):
    """解析人生阶段"""
    if isinstance(life_stages, list):
        return set(life_stages)
    if isinstance(life_stages, str):
        return set(s.strip() for s in life_stages.replace('/', ' ').replace('，', ' ').split() if s.strip())
    return set()


def calculate_similarity(movie1, movie2):
    """计算两部电影的相似度"""
    score = 0.0
    weights = {
        'genre': 0.30,      # 类型
        'director': 0.20,   # 导演
        'actors': 0.15,     # 演员
        'mbti': 0.15,       # MBTI群体
        'life_stage': 0.10, # 人生阶段
        'rating': 0.10,     # 评分相近度
    }
    
    # 1. 类型相似度 (Jaccard)
    genres1 = normalize_genre(movie1.get('genre', ''))
    genres2 = normalize_genre(movie2.get('genre', ''))
    if genres1 and genres2:
        intersection = len(genres1 & genres2)
        union = len(genres1 | genres2)
        genre_score = intersection / union if union > 0 else 0
    else:
        genre_score = 0
    score += genre_score * weights['genre']
    
    # 2. 导演相似度
    director1 = movie1.get('director', '').strip()
    director2 = movie2.get('director', '').strip()
    if director1 and director2 and director1 == director2:
        score += 1.0 * weights['director']
    
    # 3. 演员相似度 (Jaccard)
    actors1 = parse_actors(movie1.get('actors'))
    actors2 = parse_actors(movie2.get('actors'))
    if actors1 and actors2:
        intersection = len(actors1 & actors2)
        union = len(actors1 | actors2)
        actors_score = intersection / union if union > 0 else 0
        # 至少有一个共同演员才给分
        if intersection > 0:
            score += actors_score * weights['actors']
    
    # 4. MBTI群体相似度
    mbti1 = parse_mbti(movie1.get('mbti_group'))
    mbti2 = parse_mbti(movie2.get('mbti_group'))
    if mbti1 and mbti2:
        intersection = len(mbti1 & mbti2)
        union = len(mbti1 | mbti2)
        mbti_score = intersection / union if union > 0 else 0
        if intersection > 0:
            score += mbti_score * weights['mbti']
    
    # 5. 人生阶段相似度
    life1 = parse_life_stage(movie1.get('life_stage'))
    life2 = parse_life_stage(movie2.get('life_stage'))
    if life1 and life2:
        intersection = len(life1 & life2)
        union = len(life1 | life2)
        life_score = intersection / union if union > 0 else 0
        if intersection > 0:
            score += life_score * weights['life_stage']
    
    # 6. 评分相近度
    try:
        rating1 = float(movie1.get('rating', 0))
        rating2 = float(movie2.get('rating', 0))
        if rating1 > 0 and rating2 > 0:
            rating_diff = abs(rating1 - rating2)
            # 评分差0.5以内给满分，差2.0以上给0分
            rating_score = max(0, 1 - rating_diff / 2.0)
            score += rating_score * weights['rating']
    except (ValueError, TypeError):
        pass
    
    return round(score, 4)


def generate_recommendations(movies, top_n=8):
    """为每部电影生成推荐列表"""
    print(f"\n🔍 开始计算 {len(movies)} 部电影的相似度...")
    
    # 构建电影索引
    movie_dict = {m['title_cn']: m for m in movies if m.get('title_cn')}
    
    recommendations = {}
    total = len(movies)
    
    for i, movie in enumerate(movies):
        title = movie.get('title_cn', '')
        if not title:
            continue
        
        if (i + 1) % 20 == 0:
            print(f"   进度: {i+1}/{total}")
        
        # 计算与所有其他电影的相似度
        similarities = []
        for other in movies:
            other_title = other.get('title_cn', '')
            if not other_title or other_title == title:
                continue
            
            sim = calculate_similarity(movie, other)
            if sim > 0:  # 只保留有相似度的
                similarities.append({
                    'title': other_title,
                    'similarity': sim,
                    'rating': other.get('rating', 0),
                    'genre': other.get('genre', ''),
                    'year': other.get('year', ''),
                    'cover': other.get('cover_url', ''),
                })
        
        # 按相似度排序，取 top_n
        similarities.sort(key=lambda x: (x['similarity'], x['rating']), reverse=True)
        
        recommendations[title] = [
            {
                'title': s['title'],
                'rating': s['rating'],
                'genre': s['genre'],
                'year': s['year'],
                'cover': s['cover'],
                'reason': get_recommendation_reason(movie, movie_dict.get(s['title']))
            }
            for s in similarities[:top_n]
        ]
    
    print(f"   ✅ 完成! 生成了 {len(recommendations)} 部电影的推荐")
    return recommendations


def get_recommendation_reason(movie, similar_movie):
    """生成推荐理由"""
    if not similar_movie:
        return ""
    
    reasons = []
    
    # 类型相同
    genre1 = normalize_genre(movie.get('genre', ''))
    genre2 = normalize_genre(similar_movie.get('genre', ''))
    common_genres = genre1 & genre2
    if common_genres:
        reasons.append(f"类型相近")
    
    # 同一导演
    if movie.get('director') and movie.get('director') == similar_movie.get('director'):
        reasons.append(f"同导演")
    
    # 共同演员
    actors1 = parse_actors(movie.get('actors'))
    actors2 = parse_actors(similar_movie.get('actors'))
    if actors1 & actors2:
        reasons.append(f"演员阵容相似")
    
    # 都是高分
    if movie.get('rating', 0) >= 9.0 and similar_movie.get('rating', 0) >= 9.0:
        reasons.append(f"高分佳作")
    
    if reasons:
        return " · ".join(reasons[:2])
    return ""


def save_recommendations(recommendations, filename='movie_recommendations.json'):
    """保存推荐结果"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    print(f"\n💾 推荐数据已保存: {filepath}")
    return filepath


def show_demo(recommendations, movie_title="肖申克的救赎"):
    """展示推荐效果"""
    print("\n" + "=" * 60)
    print(f"📽️  Demo: \"{movie_title}\" 的推荐")
    print("=" * 60)
    
    recs = recommendations.get(movie_title, [])
    if not recs:
        print("未找到推荐数据")
        return
    
    for i, r in enumerate(recs[:6], 1):
        print(f"\n{i}. {r['title']} ⭐{r['rating']}")
        print(f"   类型: {r['genre']} | 年份: {r['year']}")
        if r['reason']:
            print(f"   理由: {r['reason']}")


def main():
    print("🎬 电影相似度推荐系统")
    print("-" * 40)
    
    # 1. 加载数据
    movies = load_movies()
    print(f"共加载 {len(movies)} 部电影")
    
    # 2. 生成推荐
    recommendations = generate_recommendations(movies, top_n=8)
    
    # 3. 保存结果
    filepath = save_recommendations(recommendations)
    
    # 4. Demo 展示
    show_demo(recommendations, "肖申克的救赎")
    print("\n")
    show_demo(recommendations, "千与千寻")
    print("\n")
    show_demo(recommendations, "盗梦空间")
    
    return recommendations


if __name__ == '__main__':
    main()
