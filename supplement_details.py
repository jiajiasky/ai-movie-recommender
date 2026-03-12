#!/usr/bin/env python3
"""
补充电影详细信息：导演、演员、剧照
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re

# 目录
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(OUTPUT_DIR, 'movies_top50.json')
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'movie_images')
STILLS_DIR = os.path.join(OUTPUT_DIR, 'movie_stills')  # 剧照目录

os.makedirs(STILLS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

IMG_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://movie.douban.com/',
}

# 加载现有数据
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

MOVIES = data['movies']

# 手动补充的详细信息（豆瓣详情页需要登录，这里用预设数据）
MOVIE_DETAILS = {
    "肖申克的救赎": {
        "director": "弗兰克·德拉邦特",
        "actors": ["蒂姆·罗宾斯", "摩根·弗里曼", "鲍勃·冈顿"],
        "duration": "142分钟",
        "country": "美国",
        "genre": "剧情 / 犯罪"
    },
    "霸王别姬": {
        "director": "陈凯歌",
        "actors": ["张国荣", "张丰毅", "巩俐", "葛优"],
        "duration": "171分钟",
        "country": "中国香港",
        "genre": "剧情 / 爱情"
    },
    "泰坦尼克号": {
        "director": "詹姆斯·卡梅隆",
        "actors": ["莱昂纳多·迪卡普里奥", "凯特·温丝莱特", "比利·赞恩"],
        "duration": "194分钟",
        "country": "美国",
        "genre": "剧情 / 爱情 / 灾难"
    },
    "阿甘正传": {
        "director": "罗伯特·泽米吉斯",
        "actors": ["汤姆·汉克斯", "罗宾·怀特", "加里·西尼斯"],
        "duration": "142分钟",
        "country": "美国",
        "genre": "剧情 / 爱情"
    },
    "千与千寻": {
        "director": "宫崎骏",
        "actors": ["柊瑠美", "入野自由", "夏木真理", "坂本龙一"],
        "duration": "125分钟",
        "country": "日本",
        "genre": "剧情 / 动画 / 奇幻"
    },
    "美丽人生": {
        "director": "罗伯托·贝尼尼",
        "actors": ["罗伯托·贝尼尼", "尼可莱塔·布拉斯基", "乔治·坎塔里尼"],
        "duration": "116分钟",
        "country": "意大利",
        "genre": "剧情 / 喜剧 / 战争"
    },
    "星际穿越": {
        "director": "克里斯托弗·诺兰",
        "actors": ["马修·麦康纳", "安妮·海瑟薇", "杰西卡·查斯坦", "迈克尔·凯恩"],
        "duration": "169分钟",
        "country": "美国 / 英国 / 加拿大",
        "genre": "剧情 / 科幻 / 冒险"
    },
    "这个杀手不太冷": {
        "director": "吕克·贝松",
        "actors": ["让·雷诺", "娜塔莉·波特曼", "加里·奥德曼", "丹尼·艾罗"],
        "duration": "110分钟",
        "country": "法国",
        "genre": "剧情 / 动作 / 犯罪"
    },
    "盗梦空间": {
        "director": "克里斯托弗·诺兰",
        "actors": ["莱昂纳多·迪卡普里奥", "约瑟夫·高登-莱维特", "艾伦·佩吉", "汤姆·哈迪"],
        "duration": "148分钟",
        "country": "美国 / 英国",
        "genre": "剧情 / 科幻 / 动作 / 冒险"
    },
    "楚门的世界": {
        "director": "彼得·威尔",
        "actors": ["金·凯瑞", "劳拉·琳妮", "诺亚·艾默里奇", "艾德·哈里斯"],
        "duration": "103分钟",
        "country": "美国",
        "genre": "剧情 / 科幻"
    },
    "辛德勒的名单": {
        "director": "史蒂文·斯皮尔伯格",
        "actors": ["连姆·尼森", "本·金斯利", "拉尔夫·费因斯", "艾伯丝·戴维兹"],
        "duration": "195分钟",
        "country": "美国",
        "genre": "剧情 / 历史 / 战争"
    },
    "忠犬八公的故事": {
        "director": "拉斯·霍尔斯道姆",
        "actors": ["理查·基尔", "萨拉·罗默尔", "琼·艾伦", "杰瑞米·雷纳"],
        "duration": "93分钟",
        "country": "美国 / 英国",
        "genre": "剧情"
    },
    "海上钢琴师": {
        "director": "朱塞佩·托纳多雷",
        "actors": ["蒂姆·罗斯", "普鲁内拉·德斯特", "比尔·努恩", "梅兰妮·蒂埃里"],
        "duration": "165分钟",
        "country": "意大利",
        "genre": "剧情 / 音乐"
    },
    "疯狂动物城": {
        "director": "拜伦·霍华德 / 瑞奇·摩尔",
        "actors": ["金妮弗·古德温", "杰森·贝特曼", "夏奇拉", "伊德里斯·艾尔巴"],
        "duration": "109分钟",
        "country": "美国",
        "genre": "剧情 / 动画 / 冒险 / 喜剧"
    },
    "三傻大闹宝莱坞": {
        "director": "拉库马·希拉尼",
        "actors": ["阿米尔·汗", "卡琳娜·卡普尔", "马达范", "沙尔曼·乔希"],
        "duration": "171分钟",
        "country": "印度",
        "genre": "剧情 / 喜剧 / 爱情 / 歌舞"
    },
    "机器人总动员": {
        "director": "安德鲁·斯坦顿",
        "actors": ["本·贝尔特", "艾丽莎·奈特", "杰夫·格尔林", "西格妮·韦弗"],
        "duration": "98分钟",
        "country": "美国",
        "genre": "剧情 / 动画 / 科幻"
    },
    "放牛班的春天": {
        "director": "克里斯托夫·巴拉蒂",
        "actors": ["热拉尔·朱诺", "让-巴蒂斯特·莫尼耶", "弗朗索瓦·贝利昂", "凯德·麦拉德"],
        "duration": "97分钟",
        "country": "法国 / 瑞士 / 德国",
        "genre": "剧情 / 音乐"
    },
    "无间道": {
        "director": "刘伟强 / 麦兆辉",
        "actors": ["刘德华", "梁朝伟", "黄秋生", "曾志伟", "郑秀文"],
        "duration": "101分钟",
        "country": "中国香港",
        "genre": "剧情 / 悬疑 / 犯罪"
    },
    "控方证人": {
        "director": "比利·怀尔德",
        "actors": ["泰隆·鲍华", "玛琳·黛德丽", "查尔斯·劳顿", "爱尔莎·兰切斯特"],
        "duration": "116分钟",
        "country": "美国",
        "genre": "剧情 / 悬疑 / 犯罪"
    },
    "寻梦环游记": {
        "director": "李·昂克里奇 / 阿德里安·莫利纳",
        "actors": ["安东尼·冈萨雷斯", "盖尔·加西亚·贝纳尔", "本杰明·布拉特", "兰德尔·克莱兹"],
        "duration": "105分钟",
        "country": "美国",
        "genre": "剧情 / 动画 / 音乐 / 家庭 / 奇幻"
    },
    "大话西游之大圣娶亲": {
        "director": "刘镇伟",
        "actors": ["周星驰", "吴孟达", "朱茵", "蔡少芬", "蓝洁瑛"],
        "duration": "95分钟",
        "country": "中国香港",
        "genre": "喜剧 / 爱情 / 奇幻 / 冒险"
    },
    "熔炉": {
        "director": "黄东赫",
        "actors": ["孔侑", "郑有美", "金志英", "金贤秀"],
        "duration": "109分钟",
        "country": "韩国",
        "genre": "剧情"
    },
    "触不可及": {
        "director": "奥利维·那卡什 / 艾力克·托兰达",
        "actors": ["弗朗索瓦·克鲁奥", "奥马尔·赛", "布丽吉特·罗西耶", "索菲·马尼阿"],
        "duration": "113分钟",
        "country": "法国",
        "genre": "剧情 / 喜剧"
    },
    "教父": {
        "director": "弗朗西斯·福特·科波拉",
        "actors": ["马龙·白兰度", "阿尔·帕西诺", "詹姆斯·凯恩", "罗伯特·杜瓦尔"],
        "duration": "175分钟",
        "country": "美国",
        "genre": "剧情 / 犯罪"
    },
    "末代皇帝": {
        "director": "贝纳尔多·贝托鲁奇",
        "actors": ["尊龙", "陈冲", "邬君梅", "彼得·奥图尔"],
        "duration": "163分钟",
        "country": "英国 / 法国 / 意大利 / 中国",
        "genre": "剧情 / 传记 / 历史"
    },
    "哈利·波特与魔法石": {
        "director": "克里斯·哥伦布",
        "actors": ["丹尼尔·雷德克里夫", "艾玛·沃特森", "鲁伯特·格林特", "艾伦·里克曼"],
        "duration": "152分钟",
        "country": "美国 / 英国",
        "genre": "奇幻 / 冒险"
    },
    "当幸福来敲门": {
        "director": "加布里尔·穆奇诺",
        "actors": ["威尔·史密斯", "贾登·史密斯", "坦迪·牛顿", "布莱恩·豪威"],
        "duration": "117分钟",
        "country": "美国",
        "genre": "剧情 / 传记 / 家庭"
    },
    "龙猫": {
        "director": "宫崎骏",
        "actors": ["日高范子", "峯田和伸", "志贺克也", "大肠广志"],
        "duration": "86分钟",
        "country": "日本",
        "genre": "剧情 / 动画 / 家庭 / 奇幻"
    },
    "活着": {
        "director": "张艺谋",
        "actors": ["葛优", "巩俐", "姜武", "牛犇"],
        "duration": "132分钟",
        "country": "中国 / 香港",
        "genre": "剧情 / 家庭"
    },
    "怦然心动": {
        "director": "罗伯·莱纳",
        "actors": ["玛德琳·卡罗尔", "卡兰·麦克奥利菲", "艾丹·奎因", "约翰·玛哈尼"],
        "duration": "90分钟",
        "country": "美国",
        "genre": "剧情 / 喜剧 / 爱情"
    },
    "蝙蝠侠：黑暗骑士": {
        "director": "克里斯托弗·诺兰",
        "actors": ["克里斯蒂安·贝尔", "希斯·莱杰", "艾伦·艾克哈特", "迈克尔·凯恩"],
        "duration": "152分钟",
        "country": "美国 / 英国",
        "genre": "剧情 / 动作 / 科幻 / 惊悚 / 犯罪"
    },
    "指环王3：王者无敌": {
        "director": "彼得·杰克逊",
        "actors": ["伊利亚·伍德", "西恩·奥斯汀", "伊恩·麦克莱恩", "维果·莫腾森", "凯特·布兰切特"],
        "duration": "201分钟",
        "country": "美国 / 新西兰",
        "genre": "剧情 / 动作 / 奇幻 / 冒险"
    },
    "我不是药神": {
        "director": "文牧野",
        "actors": ["徐峥", "王传君", "周一围", "谭卓", "章宇"],
        "duration": "117分钟",
        "country": "中国",
        "genre": "剧情 / 喜剧"
    },
    "乱世佳人": {
        "director": "维克多·弗莱明",
        "actors": ["费雯·丽", "克拉克·盖博", "奥利维娅·德哈维兰", "托马斯·米切尔"],
        "duration": "238分钟",
        "country": "美国",
        "genre": "剧情 / 爱情 / 历史 / 战争"
    },
    "飞屋环游记": {
        "director": "皮特·道格特",
        "actors": ["Jordan Nagai", "John Edwart", "Delroy Lindo", "Christopher Plummer"],
        "duration": "96分钟",
        "country": "美国",
        "genre": "剧情 / 动画 / 冒险 / 喜剧"
    },
    "让子弹飞": {
        "director": "姜文",
        "actors": ["姜文", "葛优", "周润发", "刘嘉玲", "陈坤"],
        "duration": "132分钟",
        "country": "中国",
        "genre": "剧情 / 喜剧 / 动作 / 西部"
    },
    "哈尔的移动城堡": {
        "director": "宫崎骏",
        "actors": ["倍赏千惠子", "木村拓哉", "美轮明宏", "我修院"],
        "duration": "119分钟",
        "country": "日本",
        "genre": "剧情 / 动画 / 奇幻 / 冒险"
    },
    "十二怒汉": {
        "director": " Sidney Lumet",
        "actors": ["亨利·方达", "马丁·鲍尔萨姆", "李·科布", "E.G.马绍尔"],
        "duration": "96分钟",
        "country": "美国",
        "genre": "剧情"
    },
    "海蒂和爷爷": {
        "director": "阿兰·葛斯彭纳",
        "actors": ["阿努克·斯特芬", "布鲁诺·甘茨", "昆林·艾格匹", "伊莎贝拉·垃圾桶"],
        "duration": "111分钟",
        "country": "德国 / 瑞士",
        "genre": "剧情 / 家庭"
    },
    "素媛": {
        "director": "李濬益",
        "actors": ["薛景求", "严智媛", "金海淑", "李来"],
        "duration": "123分钟",
        "country": "韩国",
        "genre": "剧情 / 家庭"
    },
    "猫鼠游戏": {
        "director": "史蒂文·斯皮尔伯格",
        "actors": ["莱昂纳多·迪卡普里奥", "汤姆·汉克斯", "克里斯托弗·普鲁默", "马丁·冯·特"],
        "duration": "141分钟",
        "country": "美国 / 加拿大",
        "genre": "剧情 / 传记 / 犯罪"
    },
    "天空之城": {
        "director": "宫崎骏",
        "actors": ["田中真弓", "横泽启子", "初井言荣", "寺道夫"],
        "duration": "125分钟",
        "country": "日本",
        "genre": "动画 / 奇幻 / 冒险"
    },
    "鬼子来了": {
        "director": "姜文",
        "actors": ["姜文", "姜宏波", "丛志军", "吴大维"],
        "duration": "139分钟",
        "country": "中国",
        "genre": "剧情 / 历史 / 战争"
    },
    "摔跤吧！爸爸": {
        "director": "尼特什·提瓦瑞",
        "actors": ["阿米尔·汗", "法缇玛·萨那·纱卡", "桑亚·玛荷塔", "阿帕尔夏克提·库尔那"],
        "duration": "161分钟",
        "country": "印度",
        "genre": "剧情 / 传记 / 运动 / 家庭"
    },
    "少年派的奇幻漂流": {
        "director": "李安",
        "actors": ["苏拉·沙玛", "伊尔凡·可汗", "塔布", "阿迪勒·侯赛因"],
        "duration": "127分钟",
        "country": "美国 / 台湾 / 香港 / 英国 / 加拿大",
        "genre": "剧情 / 奇幻 / 冒险"
    },
    "钢琴家": {
        "director": "罗曼·波兰斯基",
        "actors": ["艾德里安·布洛迪", "托马斯·克莱舒曼", "艾米莉娅·福克斯", "米哈乌·科热维茨"],
        "duration": "150分钟",
        "country": "法国 / 德国 / 英国 / 波兰",
        "genre": "剧情 / 传记 / 战争 / 音乐"
    },
    "指环王2：双塔奇兵": {
        "director": "彼得·杰克逊",
        "actors": ["伊利亚·伍德", "西恩·奥斯汀", "伊恩·麦克莱恩", "维果·莫腾森", "凯特·布兰切特"],
        "duration": "179分钟",
        "country": "美国 / 新西兰",
        "genre": "剧情 / 动作 / 奇幻 / 冒险"
    },
    "死亡诗社": {
        "director": "彼得·威尔",
        "actors": ["罗宾·威廉姆斯", "伊桑·霍克", "罗伯特·肖恩·莱纳德", "迪伦·克洛斯"],
        "duration": "128分钟",
        "country": "美国",
        "genre": "剧情"
    },
    "大话西游之月光宝盒": {
        "director": "刘镇伟",
        "actors": ["周星驰", "吴孟达", "罗家英", "莫文蔚"],
        "duration": "87分钟",
        "country": "中国香港",
        "genre": "喜剧 / 爱情 / 奇幻 / 冒险"
    },
    "何以为家": {
        "director": "娜丁·拉巴菲",
        "actors": ["赞恩·阿尔·拉菲亚", "约丹诺斯·希费罗", "博鲁瓦蒂夫·特雷杰·班科尔", "卡萨尔·艾尔·哈达里"],
        "duration": "126分钟",
        "country": "黎巴嫩 / 法国 / 美国",
        "genre": "剧情"
    },
}


def get_movie_stills(douban_id, title, max_stills=10):
    """获取电影剧照"""
    url = f"https://movie.douban.com/subject/{douban_id}/photos"
    
    stills = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 找到剧照链接
        photo_items = soup.find_all('div', class_='photo-item')
        
        for item in photo_items[:max_stills]:
            img = item.find('img')
            if img:
                # 获取大图链接
                src = img.get('src', '')
                # 替换为高清图
                still_url = src.replace('thumb', 'photo').replace('/s/', '/l/')
                stills.append(still_url)
        
        if stills:
            print(f"  ✓ 获取到 {len(stills)} 张剧照")
        
    except Exception as e:
        print(f"  ✗ 获取剧照失败: {e}")
    
    return stills


def download_still(url, filepath):
    """下载剧照"""
    try:
        resp = requests.get(url, headers=IMG_HEADERS, timeout=30)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return True
    except:
        pass
    return False


def main():
    print("=" * 50)
    print("📽️ 补充电影详细信息")
    print("=" * 50)
    
    # 提取豆瓣ID
    for movie in MOVIES:
        title = movie['title_cn']
        
        # 从URL提取豆瓣ID
        match = re.search(r'/subject/(\d+)/', movie.get('url', ''))
        if match:
            movie['douban_id'] = match.group(1)
    
    # 补充详细信息
    print("\n📋 补充导演、演员、时长等信息...")
    for movie in MOVIES:
        title = movie['title_cn']
        
        if title in MOVIE_DETAILS:
            details = MOVIE_DETAILS[title]
            movie['director'] = details['director']
            movie['actors'] = details['actors']
            movie['duration'] = details.get('duration', '')
            movie['country'] = details.get('country', '')
            movie['genre'] = details.get('genre', movie.get('genre', ''))
            print(f"  ✓ {title}: {details['director']}")
        else:
            print(f"  ⚠ {title}: 无详细数据")
    
    # 下载剧照（选取前10部演示）
    print("\n📸 下载剧照...")
    sample_movies = MOVIES[:10]
    
    for movie in sample_movies:
        title = movie['title_cn']
        douban_id = movie.get('douban_id')
        
        if not douban_id:
            continue
        
        print(f"  处理: {title}")
        
        # 获取剧照列表
        stills = get_movie_stills(douban_id, title, 10)
        
        # 下载剧照
        movie['stills'] = []
        for i, still_url in enumerate(stills):
            filename = f"{movie['rank']:02d}_{title[:10]}_{i+1}.jpg"
            filepath = os.path.join(STILLS_DIR, filename)
            
            if download_still(still_url, filepath):
                movie['stills'].append(filename)
                print(f"    ✓ 剧照 {i+1}")
        
        time.sleep(1)  # 礼貌爬取
    
    # 保存
    output = {
        'total': len(MOVIES),
        'source': 'douban.com/top250',
        'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'movies': MOVIES
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 已保存到: {DATA_FILE}")
    print(f"✓ 剧照目录: {STILLS_DIR}")


if __name__ == '__main__':
    main()
