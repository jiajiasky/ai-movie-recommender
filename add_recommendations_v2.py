#!/usr/bin/env python3
"""
为所有电影详情页添加相似电影推荐功能（嵌入推荐数据版本）
解决 file:// 协议下 fetch 无法加载 JSON 的问题
"""

import os
import re
import json

# 电影详情页目录
MOVIES_DIR = "/Users/bytedance/.openclaw/workspace/爱看电影"
RECOMMENDATIONS_FILE = os.path.join(MOVIES_DIR, "movie_recommendations.json")

# 加载推荐数据
with open(RECOMMENDATIONS_FILE, 'r', encoding='utf-8') as f:
    RECOMMENDATIONS_DATA = json.load(f)

# 推荐模块的 CSS 样式
RECOMMEND_CSS = """
        <!-- 相似推荐模块 -->
        <style>
        .recommend-section { background: var(--bg-card); border-radius: 12px; padding: 24px; margin: 20px 0; }
        .recommend-section h3 { font-size: 1.1rem; font-weight: 600; margin-bottom: 16px; }
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

        <div class="recommend-section">
            <h3>🎬 爱看此电影的人还喜欢</h3>
            <div class="recommend-grid" id="recommendGrid"></div>
        </div>
"""

# 推荐模块的 JavaScript（使用嵌入的推荐数据）
RECOMMEND_JS = """
    <script>
    // 嵌入的推荐数据（解决 file:// 协议下 fetch 跨域问题）
    var RECOMMENDATIONS_DATA = %s;

    // 从电影标题提取详情页文件名
    function getDetailFileName(title) {
        return 'detail_' + title.replace('/', '_').replace('?', '') + '.html';
    }

    // 加载相似电影推荐
    function loadRecommendations() {
        const container = document.getElementById('recommendGrid');
        if (!container) return;
        
        // 从页面标题获取当前电影名
        const titleEl = document.querySelector('.title');
        const currentMovie = titleEl ? titleEl.textContent : '';
        
        const recs = RECOMMENDATIONS_DATA[currentMovie] || [];
        
        if (recs.length === 0) {
            container.innerHTML = '<div class="recommend-empty">暂无推荐</div>';
            return;
        }
        
        container.innerHTML = recs.map(r => {
            const detailFile = getDetailFileName(r.title);
            return '<a href="' + detailFile + '" class="recommend-item">' +
                '<img class="recommend-poster" src="' + (r.cover || 'movie_images/placeholder.jpg') + '" alt="' + r.title + '" onerror="this.src=\'movie_images/placeholder.jpg\'">' +
                '<div class="recommend-info">' +
                '<div class="recommend-title">' + r.title + '</div>' +
                '<div class="recommend-meta">' +
                '<span class="recommend-rating">⭐ ' + r.rating + '</span>' +
                '<span>' + (r.year || '') + '</span>' +
                '</div>' +
                '<div class="recommend-reason">' + (r.reason || '') + '</div>' +
                '</div></a>';
        }).join('');
    }

    // 页面加载完成后加载推荐
    document.addEventListener('DOMContentLoaded', loadRecommendations);
    </script>
""" % json.dumps(RECOMMENDATIONS_DATA, ensure_ascii=False, indent=None)

def has_recommend_section(content):
    """检查是否已经有推荐模块"""
    return 'recommend-section' in content and 'recommendGrid' in content

def add_recommend_to_detail(content):
    """为详情页添加推荐模块"""
    # 检查是否已经有推荐模块
    if has_recommend_section(content):
        print("  -> 已经包含推荐模块，跳过")
        return content
    
    # 在 footer 之前插入推荐模块
    footer_pattern = r'(<div class="footer">)'
    if re.search(footer_pattern, content):
        content = re.sub(footer_pattern, RECOMMEND_CSS + r'\1', content)
        print("  -> 添加了推荐模块 CSS 和 HTML")
    else:
        content = content.replace('</div>\n</div>\n</body>', 
                                RECOMMEND_CSS + '\n</div>\n</div>\n</body>')
        print("  -> 添加了推荐模块（备选位置）")
    
    # 在 </body> 之前插入 JavaScript
    if '</body>' in content:
        content = content.replace('</body>', RECOMMEND_JS + '\n</body>')
        print("  -> 添加了推荐模块 JavaScript（嵌入数据版）")
    
    return content

def process_detail_files():
    """处理所有详情页文件"""
    # 获取所有 detail_ 开头的 HTML 文件
    detail_files = [f for f in os.listdir(MOVIES_DIR) 
                    if f.startswith('detail_') and f.endswith('.html')]
    
    print(f"找到 {len(detail_files)} 个详情页文件")
    print(f"推荐数据包含 {len(RECOMMENDATIONS_DATA)} 部电影\n")
    
    # 统计
    updated = 0
    skipped = 0
    
    for filename in sorted(detail_files):
        filepath = os.path.join(MOVIES_DIR, filename)
        
        # 读取文件
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取电影标题
        title_match = re.search(r'<h1 class="title">(.+?)</h1>', content)
        movie_title = title_match.group(1) if title_match else filename
        
        # 检查是否已经有推荐模块
        if has_recommend_section(content):
            # 如果有，检查是否是嵌入数据版本
            if 'RECOMMENDATIONS_DATA' not in content:
                print(f"更新: {movie_title}")
                # 需要更新为嵌入数据版本
                new_content = add_recommend_to_detail(content)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated += 1
            else:
                skipped += 1
            continue
        
        print(f"处理: {movie_title}")
        
        # 添加推荐模块
        new_content = add_recommend_to_detail(content)
        
        # 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        updated += 1
    
    print(f"\n完成！更新了 {updated} 个文件")

if __name__ == '__main__':
    process_detail_files()
