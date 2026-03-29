import json
import os
import random
import streamlit as st

def load_clubs_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('clubs', [])
    except FileNotFoundError:
        return []

def load_global_statistics():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'global_statistics.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"tag_affinities": {}, "profile_affinities": {}}

def update_global_matrix_with_feedback(club_id, match_score, user_profile, swipe_history):
    """
    【预留的商业化飞轮接口】
    真实环境中，此函数将连接 DB，根据 match_score 反向更新 tag_affinities 的权重。
    """
    pass

# ==========================================
# 提取出公共的评分算子，供推断和动态决策树复用
# ==========================================
def _calculate_club_scores(user_profile, swipe_history):
    clubs = load_clubs_data()
    full_stats = load_global_statistics()
    
    tag_matrix = full_stats.get('tag_affinities', {})
    profile_matrix = full_stats.get('profile_affinities', {})
    
    club_scores = {club['club_id']: 0.0 for club in clubs}
    if not clubs:
        return club_scores, clubs, tag_matrix
        
    # ==========================================
    # 修复 1：打破“刻板印象”霸权，大幅降低基础画像的权重
    # 从原来的 2.0 / 1.5 降维到 0.5 / 0.5，让“动态行为”真正主导推荐
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
    # 行为特征投射 (保持 1.0/3.0 的高权重乘数)
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
    # 修复 2：会话级“负反馈熔断”机制 (Session Blacklist)
    # 如果用户在详情页打过低分，彻底将其打入冷宫，本轮不再推荐
    # ==========================================
    disliked_clubs = st.session_state.get('disliked_clubs', set())
    for club_id in disliked_clubs:
        if club_id in club_scores:
            club_scores[club_id] = -999.0 # 强制熔断出局

    return club_scores, clubs, tag_matrix

# ==========================================
# 核心大招：动态决策树 + 探索机制
# ==========================================
def get_dynamic_tag_pairs(user_profile, swipe_history, num_pairs=4):
    club_scores, clubs, tag_matrix = _calculate_club_scores(user_profile, swipe_history)
    all_tags = list(tag_matrix.keys())
    
    # 1. 记忆机制：绝对不重复展示过去已经滑过的 tags (包含跨轮次记忆)
    used_tags = set()
    for item in swipe_history:
        used_tags.add(item['left'])
        used_tags.add(item['right'])
        
    available_tags = [t for t in all_tags if t not in used_tags]
    
    # 词库见底时的兜底重置
    if len(available_tags) < 2:
        available_tags = all_tags.copy()
        
    # 2. 决策树机制：找到当前预测的 Top 3 领先社团
    top_clubs = sorted(club_scores, key=club_scores.get, reverse=True)[:3]
    if not top_clubs and clubs:
        top_clubs = [c['club_id'] for c in clubs[:3]]
        
    # 3. 计算剩余标签的“信息增益与区分度”
    tag_scores = []
    for tag in available_tags:
        affinities = tag_matrix.get(tag, {})
        # Exploitation (利用): 这个 tag 是否能强力验证当前的高分社团？
        max_top_affinity = max([affinities.get(c, 0.0) for c in top_clubs]) if top_clubs else 0.0
        # Variance (方差): 这个 tag 在全局是否具有高度区分度？
        all_affs = list(affinities.values())
        variance = (max(all_affs) - min(all_affs)) if all_affs else 0.0
        
        # 综合试探价值
        score = (max_top_affinity * 1.5) + (variance * 1.0)
        tag_scores.append({"tag": tag, "score": score})
        
    tag_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. MAB (多臂老虎机) Epsilon-Greedy 算法组装卡片
    pairs = []
    for _ in range(num_pairs):
        if len(tag_scores) < 2:
            break
            
        # 70% 概率取最有决策价值的 tag，30% 概率纯随机取长尾/小众 tag
        if random.random() < 0.7:
            idx1, idx2 = 0, 1
        else:
            idx1 = random.randint(0, len(tag_scores) - 1)
            idx2 = random.randint(0, len(tag_scores) - 1)
            while idx1 == idx2:
                idx2 = random.randint(0, len(tag_scores) - 1)
                
        tag_left = tag_scores[idx1]["tag"]
        tag_right = tag_scores[idx2]["tag"]
        
        pairs.append({"left": tag_left, "right": tag_right})
        
        # 移除已组装的 tag
        tag_scores = [t for t in tag_scores if t["tag"] not in (tag_left, tag_right)]
        
    while len(pairs) < num_pairs:
         pairs.append({"left": "未知", "right": "探索"})
         
    return pairs

def get_top_recommended_club(user_profile, swipe_history):
    """输出最终结果"""
    club_scores, clubs, _ = _calculate_club_scores(user_profile, swipe_history)
    
    if not clubs: return None
    if sum(club_scores.values()) == 0: return clubs[0]['club_id'] 
    
    return max(club_scores, key=club_scores.get)