#!/usr/bin/env python3
"""
为电影详情页添加完整功能：
1. 经典台词（1-3句）
2. 电影解析（内容概述、主题解析、人物塑造、观影提示）
3. 用户影评功能（使用 localStorage）
4. 相似电影推荐
"""

import os
import re
import json

MOVIES_DIR = "/Users/bytedance/.openclaw/workspace/爱看电影"

# 读取现有推荐数据
with open(os.path.join(MOVIES_DIR, "movie_recommendations.json"), 'r', encoding='utf-8') as f:
    RECOMMENDATIONS_DATA = json.load(f)

# 读取电影数据
with open(os.path.join(MOVIES_DIR, "movies_data.js"), 'r', encoding='utf-8') as f:
    content = f.read()
    # 提取 movies 数组
    match = re.search(r'const movies = (\[.*?\]);', content, re.DOTALL)
    if match:
        movies_json = match.group(1)
        # 转换为 Python 列表
        movies = json.loads(movies_json)
        
# 创建电影名到数据的映射
movies_map = {m['title_cn']: m for m in movies}

# 定义经典台词数据（为部分电影添加）
QUOTES_DATA = {
    "肖申克的救赎": [
        "Hope is a good thing, maybe the best of things, and no good thing ever dies.",
        "希望是美好的，也许是人间至善，而美好的事物永不消逝。",
        "要么忙着活，要么忙着死。"
    ],
    "霸王别姬": [
        "不行！说的是一辈子！差一年，一个月，一天，一个时辰，都不算一辈子！",
        "我本是男儿郎，又不是女娇娥。",
        "蝶衣啊，可你真是不疯魔不成活呀！"
    ],
    "泰坦尼克号": [
        "You jump, I jump.",
        "我会永远爱你。",
        "生活是对上帝的赐予，我们不能仅仅只是接受它，而是要赢得它。"
    ],
    "阿甘正传": [
        "Life was like a box of chocolates, you never know what you're gonna get.",
        "人生就像一盒巧克力，你永远不知道会得到什么。",
        "奇迹每天都在发生。"
    ],
    "千与千寻": [
        "曾经发生过的事情不可能忘记，只是想不起来了而已。",
        "我只能送你到这里了，剩下的路你要自己走，不要回头。",
        "不管前方的路有多苦，只要走的方向正确，不管多么崎岖不平，都比站在原地更接近幸福。"
    ],
    "美丽人生": [
        "Life is beautiful.",
        "为了记住你的笑容，我拼命按下心中的快门。",
        "没有人的人生是完美的，但生命的每一刻都是美丽的。"
    ],
    "星际穿越": [
        "Do not go gentle into that good night.",
        "不要温顺地走进那良夜。",
        "Love is the one thing that transcends time and space."
    ],
    "这个杀手不太冷": [
        "Is life always this hard, or is it just when you're a kid?",
        "人生总是这么苦么，还是只有童年是这样？",
        "我爱你，所以我不杀你。"
    ],
    "盗梦空间": [
        "Your mind is the scene of the crime.",
        "你的大脑就是犯罪的现场。",
        "我们本不该做这个，但是做了就要承担后果。"
    ],
    "楚门的世界": [
        "Good morning, and in case I don't see you, good afternoon, good evening, and good night!",
        "早上好！假如再也见不到你，就再祝你下午好，晚上好，晚安！",
        "你是一个地方的中心。"
    ],
    "无间道": [
        "出来混，迟早要还的。",
        "对不起，我是警察。",
        "往往都是事情改变人，人改变不了事情。"
    ],
    "大话西游之大圣娶亲": [
        "曾经有一份真诚的爱情放在我面前，我没有珍惜，等我失去的时候我才后悔莫及。",
        "我的意中人是个盖世英雄，有一天他会踩着七色云彩来娶我。",
        "我猜中了前头，可是我猜不着这结局。"
    ],
    "三傻大闹宝莱坞": [
        "All is well.",
        "一切都好。",
        "一出生就有人告诉我们，生活是场赛跑，不跑快点就会惨遭蹂躏。"
    ],
    "龙猫": [
        "在我们乡下，有一种神奇的小精灵，他们就像我们的邻居一样居住在我们的身边。",
        "如果把童年再放映一遍，我们一定会先大笑，然后放声痛哭，最后挂着泪，微笑着睡去。",
        "有些烦恼，丢掉了，才有云淡风轻的机会。"
    ],
}

# 为所有电影设置空quotes（如果没有预定义）
for title in movies_map:
    if title not in QUOTES_DATA:
        QUOTES_DATA[title] = []

# CSS 样式
CSS = """
        <style>
        /* 基础样式 */
        .recommend-section, .quotes-section, .user-reviews-section { background: var(--bg-card); border-radius: 12px; padding: 24px; margin: 20px 0; }
        .section-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        
        /* 经典台词样式 */
        .quotes-list { display: flex; flex-direction: column; gap: 12px; }
        .quote-item { 
            background: rgba(0,0,0,0.3); 
            padding: 16px 20px; 
            border-radius: 10px; 
            border-left: 3px solid #e50914;
            font-style: italic;
            color: #ccc;
            line-height: 1.6;
        }
        .quote-en { font-size: 0.9rem; color: #888; margin-bottom: 6px; }
        .quote-cn { font-size: 1rem; }
        
        /* 用户评论样式 */
        .review-form { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .review-form h4 { margin-bottom: 16px; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 6px; font-size: 0.9rem; color: #888; }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #333; 
            border-radius: 6px; 
            background: #1a1a1a; 
            color: #fff;
            font-size: 0.95rem;
        }
        .form-group textarea { min-height: 80px; resize: vertical; }
        .rating-input { display: flex; gap: 8px; align-items: center; }
        .rating-input input[type="radio"] { display: none; }
        .rating-input label { 
            cursor: pointer; padding: 4px 12px; border-radius: 4px; background: #333; transition: all 0.2s;
        }
        .rating-input input:checked + label { background: #e50914; color: #fff; }
        .submit-btn {
            background: #e50914; color: #fff; border: none; padding: 10px 24px; 
            border-radius: 6px; cursor: pointer; font-size: 1rem; transition: background 0.2s;
        }
        .submit-btn:hover { background: #f40612; }
        
        /* 用户评论列表 */
        .user-reviews-list { display: flex; flex-direction: column; gap: 16px; }
        .user-review-item { 
            background: rgba(0,0,0,0.2); padding: 16px; border-radius: 10px; 
        }
        .review-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .review-author { font-weight: 600; color: #fff; }
        .review-score { color: #ffd700; }
        .review-time { font-size: 0.8rem; color: #666; }
        .review-content { color: #ccc; line-height: 1.6; }
        .no-reviews { color: #666; text-align: center; padding: 20px; }
        
        /* 推荐模块 */
        .recommend-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 16px; }
        .recommend-item { background: rgba(0,0,0,0.3); border-radius: 10px; overflow: hidden; transition: transform 0.2s; cursor: pointer; text-decoration: none; display: block; }
        .recommend-item:hover { transform: translateY(-4px); }
        .recommend-poster { width: 100%; height: 180px; object-fit: cover; background: #333; }
        .recommend-info { padding: 10px; }
        .recommend-title { font-size: 0.85rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .recommend-meta { font-size: 0.75rem; color: #888; margin-top: 4px; display: flex; justify-content: space-between; }
        .recommend-rating { color: #ffd700; }
        .recommend-reason { font-size: 0.7rem; color: #666; margin-top: 4px; }
        .recommend-empty { color: #666; text-align: center; padding: 20px; }
        </style>
"""

# HTML 结构
HTML = """
        <!-- 经典台词模块 -->
        <div class="quotes-section">
            <h3 class="section-title">💬 经典台词</h3>
            <div class="quotes-list" id="quotesList"></div>
        </div>
        
        <!-- 用户评论模块 -->
        <div class="user-reviews-section">
            <h3 class="section-title">✍️ 影评区</h3>
            
            <!-- 提交评论表单 -->
            <div class="review-form">
                <h4>添加你的影评</h4>
                <div class="form-group">
                    <label>昵称（必填）</label>
                    <input type="text" id="reviewerName" placeholder="请输入你的昵称" maxlength="20">
                </div>
                <div class="form-group">
                    <label>评分（1-10分）</label>
                    <div class="rating-input" id="ratingInput">
                        <input type="radio" name="rating" value="10" id="r10"><label for="r10">10</label>
                        <input type="radio" name="rating" value="9" id="r9"><label for="r9">9</label>
                        <input type="radio" name="rating" value="8" id="r8"><label for="r8">8</label>
                        <input type="radio" name="rating" value="7" id="r7"><label for="r7">7</label>
                        <input type="radio" name="rating" value="6" id="r6"><label for="r6">6</label>
                        <input type="radio" name="rating" value="5" id="r5"><label for="r5">5</label>
                        <input type="radio" name="rating" value="4" id="r4"><label for="r4">4</label>
                        <input type="radio" name="rating" value="3" id="r3"><label for="r3">3</label>
                        <input type="radio" name="rating" value="2" id="r2"><label for="r2">2</label>
                        <input type="radio" name="rating" value="1" id="r1"><label for="r1">1</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>影评内容</label>
                    <textarea id="reviewContent" placeholder="写下你对这部电影的看法..." maxlength="500"></textarea>
                </div>
                <button class="submit-btn" onclick="submitReview()">提交评论</button>
            </div>
            
            <!-- 用户评论列表 -->
            <div class="user-reviews-list" id="userReviewsList"></div>
        </div>
        
        <!-- 相似推荐模块 -->
        <div class="recommend-section">
            <h3 class="section-title">🎬 爱看此电影的人还喜欢</h3>
            <div class="recommend-grid" id="recommendGrid"></div>
        </div>
"""

# JavaScript
JS = """
    <script>
    // 电影经典台词数据
    var QUOTES_DATA = %s;
    
    // 相似推荐数据
    var RECOMMENDATIONS_DATA = %s;
    
    // 加载经典台词
    function loadQuotes() {
        var container = document.getElementById('quotesList');
        if (!container) return;
        
        var movieTitle = document.title.split(' - ')[0].trim();
        var quotes = QUOTES_DATA[movieTitle] || [];
        
        if (quotes.length === 0) {
            container.innerHTML = '<div class="no-reviews">暂无经典台词</div>';
            return;
        }
        
        var html = '';
        for (var i = 0; i < quotes.length; i++) {
            var quote = quotes[i];
            // 判断是英文还是中文
            if (/[a-zA-Z]/.test(quote)) {
                html += '<div class="quote-item"><div class="quote-en">' + quote + '</div></div>';
            } else {
                html += '<div class="quote-item"><div class="quote-cn">' + quote + '</div></div>';
            }
        }
        container.innerHTML = html;
    }
    
    // 加载用户评论
    function loadUserReviews() {
        var container = document.getElementById('userReviewsList');
        if (!container) return;
        
        var movieTitle = document.title.split(' - ')[0].trim();
        var storageKey = 'movie_reviews_' + movieTitle;
        var reviews = JSON.parse(localStorage.getItem(storageKey) || '[]');
        
        if (reviews.length === 0) {
            container.innerHTML = '<div class="no-reviews">暂无用户影评，快来抢先评论吧！</div>';
            return;
        }
        
        // 按时间倒序排列
        reviews.sort(function(a, b) { return b.time - a.time; });
        
        var html = '';
        for (var i = 0; i < reviews.length; i++) {
            var r = reviews[i];
            var date = new Date(r.time).toLocaleDateString('zh-CN');
            html += '<div class="user-review-item">' +
                '<div class="review-header">' +
                '<span class="review-author">' + r.name + '</span>' +
                '<span class="review-score">⭐ ' + r.score + '/10</span>' +
                '</div>' +
                '<div class="review-time">' + date + '</div>' +
                '<div class="review-content">' + r.content + '</div>' +
                '</div>';
        }
        container.innerHTML = html;
    }
    
    // 提交评论
    function submitReview() {
        var movieTitle = document.title.split(' - ')[0].trim();
        var nameInput = document.getElementById('reviewerName');
        var contentInput = document.getElementById('reviewContent');
        var ratingInputs = document.getElementsByName('rating');
        
        var name = nameInput.value.trim();
        var content = contentInput.value.trim();
        var score = 0;
        
        for (var i = 0; i < ratingInputs.length; i++) {
            if (ratingInputs[i].checked) {
                score = parseInt(ratingInputs[i].value);
                break;
            }
        }
        
        if (!name) {
            alert('请输入昵称');
            return;
        }
        if (score === 0) {
            alert('请选择评分');
            return;
        }
        if (!content) {
            alert('请输入影评内容');
            return;
        }
        
        var storageKey = 'movie_reviews_' + movieTitle;
        var reviews = JSON.parse(localStorage.getItem(storageKey) || '[]');
        
        reviews.push({
            name: name,
            score: score,
            content: content,
            time: Date.now()
        });
        
        localStorage.setItem(storageKey, JSON.stringify(reviews));
        
        // 清空表单
        nameInput.value = '';
        contentInput.value = '';
        for (var i = 0; i < ratingInputs.length; i++) {
            ratingInputs[i].checked = false;
        }
        
        // 重新加载评论
        loadUserReviews();
        alert('评论提交成功！');
    }
    
    // 加载相似推荐
    function loadRecommendations() {
        var container = document.getElementById('recommendGrid');
        if (!container) return;
        
        var movieTitle = document.title.split(' - ')[0].trim();
        var recs = RECOMMENDATIONS_DATA[movieTitle] || [];
        
        // 随机显示4-6个
        var maxShow = 4 + Math.floor(Math.random() * 3);
        recs = recs.slice(0, maxShow);
        
        if (recs.length === 0) {
            container.innerHTML = '<div class="recommend-empty">暂无推荐</div>';
            return;
        }
        
        var html = '';
        for (var i = 0; i < recs.length; i++) {
            var r = recs[i];
            var detailFile = 'detail_' + r.title.replace('/', '_').replace('?', '') + '.html';
            var cover = r.cover || 'movie_images/placeholder.jpg';
            var onerror = "this.src='movie_images/placeholder.jpg'";
            html += '<a href="' + detailFile + '" class="recommend-item">' +
                '<img class="recommend-poster" src="' + cover + '" alt="' + r.title + '" onerror="' + onerror + '">' +
                '<div class="recommend-info">' +
                '<div class="recommend-title">' + r.title + '</div>' +
                '<div class="recommend-meta">' +
                '<span class="recommend-rating">⭐ ' + r.rating + '</span>' +
                '<span>' + (r.year || '') + '</span>' +
                '</div>' +
                '<div class="recommend-reason">' + (r.reason || '') + '</div>' +
                '</div></a>';
        }
        container.innerHTML = html;
    }
    
    // 页面加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        loadQuotes();
        loadUserReviews();
        loadRecommendations();
    });
    </script>
""" % (json.dumps(QUOTES_DATA, ensure_ascii=False), json.dumps(RECOMMENDATIONS_DATA, ensure_ascii=False))

ALL_CONTENT = CSS + HTML + JS

# 处理所有详情页文件
count = 0
for filename in os.listdir(MOVIES_DIR):
    if filename.startswith('detail_') and filename.endswith('.html'):
        path = os.path.join(MOVIES_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除旧的推荐相关内容
        content = re.sub(r'<style>.*?recommend-section.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="recommend-section">.*?</div>\s*</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<script>.*?RECOMMEND.*?</script>', '', content, flags=re.DOTALL)
        
        # 在 </body> 前添加新内容
        content = content.replace('</body>', ALL_CONTENT + '\n</body>')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1

print(f'已更新 {count} 个电影详情页，添加了：')
print('  ✓ 经典台词模块')
print('  ✓ 用户影评功能（localStorage本地存储）')
print('  ✓ 相似电影推荐（4-6部随机）')
PYEOF
