#!/usr/bin/env python3
"""
Vibe 推荐算法
基于 MBTI + 人生阶段 + 用户行为
"""

import json
import random
from movie_tags import MOVIE_TAGS, MBTI_PREFERENCES, LIFE_STAGE_PREFERENCES, GENRE_MAP

# 加载电影数据
with open('movies_top50.json', 'r', encoding='utf-8') as f:
    MOVIES = json.load(f)['movies']

# 构建电影索引
MOVIE_DICT = {m['title_cn']: m for m in MOVIES}


class VibeRecommender:
    """Vibe 推荐器"""
    
    def __init__(self):
        self.movies = MOVIES
        self.user_mbti = None
        self.user_life_stage = None
        self.user_age = None
        self.behavior = {}  # {movie_title: 'like'/'watched'/'dislike'}
    
    def set_user(self, mbti: str, life_stage: str, age: int = None):
        """设置用户画像"""
        self.user_mbti = mbti.upper()
        self.user_life_stage = life_stage
        self.user_age = age
    
    def add_behavior(self, movie_title: str, action: str):
        """添加用户行为"""
        # 模糊匹配电影名
        for m in self.movies:
            if movie_title in m['title_cn'] or m['title_cn'] in movie_title:
                self.behavior[m['title_cn']] = action
                break
    
    def _get_mbti_score(self, movie) -> float:
        """计算 MBTI 匹配分数"""
        title = movie['title_cn']
        
        # 精确匹配
        if title in MOVIE_TAGS:
            tags = MOVIE_TAGS[title]
            if self.user_mbti in tags.get('mbti', []):
                return 1.0
        
        # 基于类型推断
        genre = movie.get('genre', '')
        if not genre:
            # 尝试从标题推断
            genre = self._infer_genre(title)
        
        if not genre:
            return 0.5  # 默认分数
        
        # MBTI 各维度匹配
        score = 0.5
        mbti_chars = list(self.user_mbti)
        
        for i, dim in enumerate(['E', 'S', 'T', 'J']):  # E/I, S/N, T/F, J/P
            if i < len(mbti_chars):
                char = mbti_chars[i]
                pref = MBTI_PREFERENCES.get(dim + char, [])
                if any(g in genre for g in pref):
                    score += 0.15
        
        return min(score, 1.0)
    
    def _infer_genre(self, title: str) -> str:
        """从标题/年份推断类型"""
        # 简单规则
        hints = {
            "千与千寻": "动画", "龙猫": "动画", "天空之城": "动画",
            "哈尔的移动城堡": "动画", "飞屋环游记": "动画", "疯狂动物城": "动画",
            "机器人总动员": "动画", "寻梦环游记": "动画", "哈利": "奇幻",
            "指环王": "奇幻", "霍比特人": "奇幻",
            "星际穿越": "科幻", "盗梦空间": "科幻",
            "泰坦尼克号": "爱情", "怦然心动": "爱情",
            "肖申克": "剧情", "霸王别姬": "剧情", "阿甘正传": "剧情",
            "辛德勒": "剧情", "教父": "犯罪", "无间道": "犯罪",
            "让子弹飞": "动作", "摔跤吧": "喜剧",
        }
        for key, genre in hints.items():
            if key in title:
                return genre
        return ""
    
    def _get_life_stage_score(self, movie) -> float:
        """计算人生阶段匹配分数"""
        title = movie['title_cn']
        
        if title in MOVIE_TAGS:
            tags = MOVIE_TAGS[title]
            if self.user_life_stage in tags.get('life_stage', []):
                return 1.0
        
        return 0.5  # 默认
    
    def recommend(self, top_n: int = 5) -> list:
        """推荐电影"""
        results = []
        
        for movie in self.movies:
            # 跳过已看过的
            if self.behavior.get(movie['title_cn']) == 'watched':
                continue
            
            # 计算综合分数
            mbti_score = self._get_mbti_score(movie)
            life_score = self._get_life_stage_score(movie)
            
            # 行为调整
            behavior = self.behavior.get(movie['title_cn'], '')
            behavior_score = 0
            if behavior == 'like':
                behavior_score = 0.3
            elif behavior == 'dislike':
                behavior_score = -0.5
            
            # 评分权重
            rating_score = movie.get('rating', 9.0) / 10.0
            
            # 综合分数
            total_score = (
                mbti_score * 0.35 +
                life_score * 0.30 +
                rating_score * 0.25 +
                behavior_score * 0.10
            )
            
            # 惩罚已不喜欢的
            if behavior == 'dislike':
                total_score = -1
            
            results.append({
                'movie': movie,
                'score': round(total_score, 3),
                'mbti_match': round(mbti_score, 2),
                'life_match': round(life_score, 2),
                'reasons': self._get_reasons(movie, mbti_score, life_score)
            })
        
        # 排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_n]
    
    def _get_reasons(self, movie, mbti_score, life_score) -> list:
        """生成推荐理由"""
        reasons = []
        title = movie['title_cn']
        
        # 评分高
        if movie.get('rating', 0) >= 9.3:
            reasons.append(f"⭐ 豆瓣高分 {movie['rating']}")
        
        # MBTI 匹配
        if mbti_score >= 0.8:
            reasons.append("🎯 MBTI 高度匹配")
        elif mbti_score >= 0.6:
            reasons.append("👍 MBTI 匹配")
        
        # 人生阶段匹配
        if life_score >= 0.8:
            reasons.append("💡 非常适合当前人生阶段")
        elif life_score >= 0.6:
            reasons.append("💡 适合当前阶段")
        
        # 经典电影
        if movie.get('year') and int(movie.get('year', 0)) < 2000:
            reasons.append("🎬 经典佳作")
        
        return reasons[:3]  # 最多3条


def demo():
    """演示推荐"""
    print("=" * 60)
    print("🎬 Vibe 推荐算法演示")
    print("=" * 60)
    
    # 创建推荐器
    recommender = VibeRecommender()
    
    # 测试用例
    test_cases = [
        {"mbti": "INTJ", "life_stage": "职业", "name": "职场精英 INTJ"},
        {"mbti": "ENFP", "life_stage": "成长", "name": "成长中 ENFP"},
        {"mbti": "INFP", "life_stage": "自我实现", "name": "文艺青年 INFP"},
        {"mbti": "ESFJ", "life_stage": "家庭", "name": "家庭型 ESFJ"},
    ]
    
    for tc in test_cases:
        print(f"\n👤 用户: {tc['name']}")
        print("-" * 40)
        
        recommender.set_user(tc['mbti'], tc['life_stage'])
        
        # 添加一些行为
        recommender.add_behavior("肖申克的救赎", "watched")
        recommender.add_behavior("星际穿越", "like")
        
        results = recommender.recommend(5)
        
        for i, r in enumerate(results, 1):
            m = r['movie']
            print(f"\n{i}. {m['title_cn']} ⭐{m['rating']}")
            print(f"   匹配度: {r['score']:.0%} | {', '.join(r['reasons'])}")


if __name__ == '__main__':
    demo()
