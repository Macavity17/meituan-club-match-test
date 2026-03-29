import json
import os
import random
import streamlit as st

# ==========================================
# 优化 1：引入缓存机制，模拟生产环境高性能读取
# ==========================================
@st.cache_data
def load_clubs_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('clubs', [])
    except FileNotFoundError:
        return []

@st.cache_data
def load_global_statistics():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'global_statistics.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tag_affinities": {}, "profile_affinities": {}}

def update_global_matrix_with_feedback(club_id, match_score, user_profile, swipe_history):
    """【预留接口】用于未来反向向 DB 回传数据权重"""
    pass

def _calculate_club_scores(user_profile, swipe_history):
    clubs = load_clubs_data()
    full_stats = load_global_statistics()
    
    tag_matrix = full_stats.get('tag_affinities', {})
    profile_matrix = full_stats.get('profile_affinities', {})
    
    # 初始化分数
    club_scores = {club['club_id']: 0.0 for club in clubs}
    if not clubs:
        return club_scores, clubs, tag_matrix

    # ==========================================
    # 核心修复 1：硬性地理围栏 (Campus Recall Filter)
    # 实现你在 README 中承诺的“硬召回”逻辑
    # ==========================================
    user_campus = user_profile.get('campus', '')
    
    # ==========================================
    # 基础画像评分 (权重 0.5)
    # ==========================================
    time_commit = user_profile.get('time_commit', '')
    mbti = user_profile.get('mbti', '')
    
    if time_commit in profile_matrix:
        for club_id, prob in profile_matrix[time_commit].items():
            if club_id in club_scores: club_scores[club_id] += (prob * 0.5) 
            
    if mbti in profile_matrix:
        for club_id, prob in profile_matrix[mbti].items():
            if club_id in club_scores: club_scores[club_id] += (prob * 0.5)

    # ==========================================
    # 行为特征投射 (权重 1.0/3.0)
    # ==========================================
    for item in swipe_history:
        choice = item['choice']
        left_tag = item['left']
        right_tag = item['right']
        
        weight = 0.0
        active_tag = None
        if "绝对偏向" in choice:
            weight = 3.0
            active_tag = left_tag if left_tag in choice else right_tag
        elif "偏向" in choice:
            weight = 1.0
            active_tag = left_tag if left_tag in choice else right_tag
            
        if weight > 0 and active_tag and active_tag in tag_matrix:
            for club_id, historical_prob in tag_matrix[active_tag].items():
                if club_id in club_scores:
                    club_scores[club_id] += (weight * historical_prob)

    # ==========================================
    # 核心修复 2：跨校区惩罚逻辑 (Hard Recall Penalty)
    # 如果用户校区与社团主要活动地点不符，大幅扣分，模拟召回过滤
    # ==========================================
    for club in clubs:
        cid = club['club_id']
        # 简单逻辑：如果用户选了校区，但社团描述/标签里没有包含这个校区关键词，则降权
        if user_campus and user_campus != "其他":
            # 这里的逻辑可以根据你的 mock_clubs.json 结构微调
            # 假设社团的活动校区信息隐藏在描述或标签中
            club_text = club.get('detailed_description', '') + "".join(club.get('tags', []))
            if user_campus not in club_text and "全校" not in club_text:
                club_scores[cid] -= 5.0 # 强力降权

    # ==========================================
    # 负反馈熔断 (Session Blacklist)
    # ==========================================
    disliked_clubs = st.session_state.get('disliked_clubs', set())
    for club_id in disliked_clubs:
        if club_id in club_scores:
            club_scores[club_id] = -999.0 

    return club_scores, clubs, tag_matrix

def get_dynamic_tag_pairs(user_profile, swipe_history, num_pairs=4):
    """
    动态决策树生成器。
    
    """
    club_scores, clubs, tag_matrix = _calculate_club_scores(user_profile, swipe_history)
    all_tags = list(tag_matrix.keys())
    
    # 1. 记忆机制：绝对不重复展示
    used_tags = set()
    for item in swipe_history:
        used_tags.add(item['left'])
        used_tags.add(item['right'])
        
    available_tags = [t for t in all_tags if t not in used_tags]
    if len(available_tags) < 2:
        available_tags = all_tags.copy()
        
    # 2. 找到 Top 3 领先社团
    top_clubs = sorted(club_scores, key=club_scores.get, reverse=True)[:3]
        
    # 3. 标签信息增益评分
    tag_scores = []
    for tag in available_tags:
        affinities = tag_matrix.get(tag, {})
        max_top_affinity = max([affinities.get(c, 0.0) for c in top_clubs]) if top_clubs else 0.0
        all_affs = list(affinities.values())
        variance = (max(all_affs) - min(all_affs)) if all_affs else 0.0
        
        # 权重公式：利用度 + 区分度
        score = (max_top_affinity * 1.5) + (variance * 1.0)
        tag_scores.append({"tag": tag, "score": score})
        
    tag_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. Epsilon-Greedy 策略
    pairs = []
    for _ in range(num_pairs):
        if len(tag_scores) < 2: break
            
        if random.random() < 0.7:
            idx1, idx2 = 0, 1 # 取价值最高的
        else:
            idx1 = random.randint(0, len(tag_scores) - 1)
            idx2 = random.randint(0, len(tag_scores) - 1)
            while idx1 == idx2: idx2 = random.randint(0, len(tag_scores) - 1)
                
        tag_left = tag_scores[idx1]["tag"]
        tag_right = tag_scores[idx2]["tag"]
        pairs.append({"left": tag_left, "right": tag_right})
        tag_scores = [t for t in tag_scores if t["tag"] not in (tag_left, tag_right)]
        
    # 兜底填充：不再使用“未知/探索”，而是随机从全库取标签
    while len(pairs) < num_pairs:
         r_tags = random.sample(all_tags, 2)
         pairs.append({"left": r_tags[0], "right": r_tags[1]})
         
    return pairs

def get_top_recommended_club(user_profile, swipe_history):
    """最终精排输出"""
    club_scores, clubs, _ = _calculate_club_scores(user_profile, swipe_history)
    if not clubs: return None
    return max(club_scores, key=club_scores.get)