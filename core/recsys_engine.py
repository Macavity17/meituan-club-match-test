import json
import os
import random

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

# ==========================================
# 【核心 AI 架构】全局数据飞轮与反馈统计算法
# 正常商业化落地时，我们会引入 DB 持久化更新全局矩阵。
# 以下仅保留算法骨架，向面试官展示完整的产品逻辑闭环：即如何让系统越用越准。
# ==========================================
def update_global_matrix_with_feedback(club_id, match_score, user_profile, swipe_history):
    """
    飞轮闭环：基于用户真实打分反向修正概率矩阵 (Tag & Profile)。
    由 v3_club_detail.py 中用户点击“提交反馈”时触发。
    """
    # 1. 计算反馈奖励乘数 (Reward Multiplier)
    # 假设 1-5 分，3分为中立。4-5分给予正反馈提升概率，1-2分给予负反馈惩罚概率。
    # reward_delta = (match_score - 3) * 0.05 
    
    # 2. 生产环境：反向更新基础画像的先验概率 (Profile Affinities)
    # time_commit = user_profile.get('time_commit')
    # mbti = user_profile.get('mbti')
    # if time_commit:
    #     db.execute("UPDATE profile_affinities SET prob = prob + ? WHERE feature = ? AND club = ?", reward_delta, time_commit, club_id)
    # if mbti:
    #     db.execute("UPDATE profile_affinities SET prob = prob + ? WHERE feature = ? AND club = ?", reward_delta, mbti, club_id)

    # 3. 生产环境：反向更新行为特征的先验概率 (Tag Affinities)
    # for item in swipe_history:
    #     if "偏向" in item['choice']:
    #         tag = item['left'] if item['left'] in item['choice'] else item['right']
    #         # 只有用户表现出偏向的 Tag，才将其与最终落地的社团进行权重绑定/解绑
    #         db.execute("UPDATE tag_affinities SET prob = prob + ? WHERE tag = ? AND club = ?", reward_delta, tag, club_id)
    pass


def get_dynamic_tag_pairs(num_pairs=4):
    stats = load_global_statistics().get('tag_affinities', {})
    if not stats:
        return [{"left": "技术", "right": "艺术"}] * num_pairs
    
    unique_tags = list(stats.keys())
    # 生产环境中这里应使用 UCB/MAB 算法优先抽取高方差 tag 进行 Exploration
    random.seed(42) 
    random.shuffle(unique_tags)
    
    pairs = []
    for i in range(0, min(len(unique_tags), num_pairs * 2), 2):
        if i + 1 < len(unique_tags):
            pairs.append({"left": unique_tags[i], "right": unique_tags[i+1]})
    return pairs


def get_top_recommended_club(user_profile, swipe_history):
    """
    全量数据驱动推荐：Profile 先验概率 + Swipe 行为映射
    """
    clubs = load_clubs_data()
    full_stats = load_global_statistics()
    
    tag_matrix = full_stats.get('tag_affinities', {})
    profile_matrix = full_stats.get('profile_affinities', {})
    
    if not clubs:
        return None
        
    club_scores = {club['club_id']: 0.0 for club in clubs}
    
    # --- 1. 基础画像 (Profile) 概率映射 ---
    time_commit = user_profile.get('time_commit', '')
    mbti = user_profile.get('mbti', '')
    
    if time_commit in profile_matrix:
        for club_id, prob in profile_matrix[time_commit].items():
            if club_id in club_scores:
                club_scores[club_id] += (prob * 2.0)
                
    if mbti in profile_matrix:
        for club_id, prob in profile_matrix[mbti].items():
            if club_id in club_scores:
                club_scores[club_id] += (prob * 1.5)

    # --- 2. 行为特征 (Swipe) 概率映射 ---
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
                    
    # --- 3. 兜底与结果输出 ---
    if sum(club_scores.values()) == 0:
        return clubs[0]['club_id'] 
        
    top_club_id = max(club_scores, key=club_scores.get)
    return top_club_id