import streamlit as st
from core.state_manager import navigate_to
from core.recsys_engine import get_dynamic_tag_pairs, get_top_recommended_club

def render():
    st.title("🎴 发现你的热爱")
    
    # ==========================================
    # 顶部全局导航栏
    # ==========================================
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 发现主页", use_container_width=True):
            navigate_to('home_dashboard')
    with col_nav2:
        st.button("🎴 沉浸式 AI 匹配", use_container_width=True, disabled=True)
    with col_nav3:
        if st.button("👤 我的与投递", use_container_width=True):
            navigate_to('profile')
    st.markdown("---")

    # 初始化状态机
    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []
        
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
        
    # 1. 结合历史记录，动态获取拔河卡片 (新版 AI 决策树引擎)
    if 'dynamic_pairs' not in st.session_state:
        with st.spinner("🧠 算法正在根据你的潜意识，实时生成深度测试分支..."):
            st.session_state.dynamic_pairs = get_dynamic_tag_pairs(
                user_profile=st.session_state.get('user_profile', {}),
                swipe_history=st.session_state.swipe_history,
                num_pairs=4
            )
        
    current_idx = st.session_state.swipe_index
    total_cards = len(st.session_state.dynamic_pairs)
    
    # 2. 核心流转逻辑：保留了最灵魂的 Slider 拔河交互
    if current_idx < total_cards:
        st.markdown(f"**匹配进度：{current_idx + 1} / {total_cards}**")
        st.markdown("凭借第一直觉，选择你更偏好的社团基因（Tag）：")
        
        pair = st.session_state.dynamic_pairs[current_idx]
        
        # 恢复原版极致精简的 Tug of War 刻度
        choice = st.select_slider(
            label="你的偏好是？",
            options=[
                f"👈 绝对偏向：{pair['left']}", 
                f"偏向：{pair['left']}", 
                "⚖️ 都可以 / 无感", 
                f"偏向：{pair['right']}", 
                f"绝对偏向：{pair['right']} 👉"
            ],
            value="⚖️ 都可以 / 无感",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 提交当前打分
        if st.button("下一张 ➡️", type="primary", use_container_width=True):
            st.session_state.swipe_history.append({
                "left": pair['left'],
                "right": pair['right'],
                "choice": choice
            })
            st.session_state.swipe_index += 1
            st.rerun()
            
    else:
        # ==========================================
        # 3. 算法计算与拦截页面 (恢复了重洗功能)
        # ==========================================
        with st.spinner('🎯 正在锁定最佳匹配项...'):
            best_club_id = get_top_recommended_club(
                st.session_state.get('user_profile', {}), 
                st.session_state.swipe_history
            )
            
        st.session_state.current_club_view = best_club_id
        st.session_state.from_ai_recommendation = True
        
        st.success("✨ 基于你的直觉与基础属性，AI 大脑已计算出最高得分社团！")
        st.info("侧边栏 AI 助手已就绪，正在为你生成个性化推荐理由 👇")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👀 立即查看专属推荐", type="primary", use_container_width=True):
                # 进去看之前，清空当前的题目对和下标，确保下次退出来时能重新触发决策树
                del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                navigate_to('club_detail')
        with col2:
            if st.button("❌ 感觉不对，重洗标签", use_container_width=True):
                # 清除当前卡片池和历史，重新生成新的一批 Tags (基于探索机制)
                del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                st.session_state.swipe_history = []  # 核心：清空历史，让决策树重新开局
                st.rerun()