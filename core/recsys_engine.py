import json
import os
import random

def load_clubs_data():
    """从唯一的单点数据源读取所有社团信息"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('clubs', [])
    except FileNotFoundError:
        return []

def get_dynamic_tag_pairs(num_pairs=4):
    """
    动态生成极简 Tag 拔河卡片
    直接遍历数据库，提取所有社团的 tags，打乱后两两配对，拒绝硬编码。
    """
    clubs = load_clubs_data()
    if not clubs:
        return [{"left": "技术", "right": "艺术"}] * num_pairs
    
    all_tags = []
    for club in clubs:
        # 过滤掉“高/低耗能”这类不适合放在拔河里的基础属性 tag
        valid_tags = [tag for tag in club.get('tags', []) if "耗能" not in tag]
        all_tags.extend(valid_tags)
    
    # 去重并打乱
    unique_tags = list(set(all_tags))
    random.seed(42) # 仅为 Demo 演示稳定性固定种子，生产环境移除即可
    random.shuffle(unique_tags)
    
    pairs = []
    # 两两配对
    for i in range(0, min(len(unique_tags), num_pairs * 2), 2):
        if i + 1 < len(unique_tags):
            pairs.append({"left": unique_tags[i], "right": unique_tags[i+1]})
            
    return pairs

def get_top_recommended_club(user_profile, swipe_history):
    """
    数据飞轮核心：融合 V1 画像特征 + V2 滑动行为特征
    """
    clubs = load_clubs_data()
    if not clubs:
        return None
        
    # 初始化候选社团得分池
    club_scores = {club['club_id']: 0.0 for club in clubs}
    
    # ==========================================
    # 特征 1：合并 V1 的基础画像 (隐式关联匹配)
    # ==========================================
    time_commit = user_profile.get('time_commit', '')
    mbti = user_profile.get('mbti', '')
    
    for club in clubs:
        tags = club.get('tags', [])
        
        # 投入时间与社团耗能度关联
        if "6小时" in time_commit and "高耗能" in tags:
            club_scores[club['club_id']] += 2.0
        elif "1-2小时" in time_commit and ("低耗能" in tags or "休闲" in tags):
            club_scores[club['club_id']] += 2.0
            
        # MBTI 与 极客/社交 属性的隐式关联 (Mock 粗排逻辑)
        if mbti in ["INTJ", "INTP", "ISTJ"] and ("极客" in tags or "数据科学" in tags):
            club_scores[club['club_id']] += 1.5
        elif mbti in ["ENFJ", "ESFJ", "ENFP"] and ("公益" in tags or "社交" in tags):
            club_scores[club['club_id']] += 1.5

    # ==========================================
    # 特征 2：解析 V2 的行为序列 (方差与极性权重)
    # ==========================================
    for item in swipe_history:
        choice = item['choice']
        left_tag = item['left']
        right_tag = item['right']
        
        weight = 0.0
        active_tag = None
        
        # 极性探索机制：方差大的选择给予高权重
        if "绝对偏向" in choice:
            weight = 3.0
            active_tag = left_tag if left_tag in choice else right_tag
        elif "偏向" in choice:
            weight = 1.0
            active_tag = left_tag if left_tag in choice else right_tag
            
        # 命中“中立”，weight 保持为 0，有效降低噪音影响
        
        # 将得分精准映射回包含该 tag 的所有社团
        if weight > 0 and active_tag:
            for club in clubs:
                if active_tag in club.get('tags', []):
                    club_scores[club['club_id']] += weight
                    
    # ==========================================
    # 结果输出
    # ==========================================
    if sum(club_scores.values()) == 0:
        return clubs[0]['club_id'] # 极端情况防崩溃兜底
        
    top_club_id = max(club_scores, key=club_scores.get)
    return top_club_id