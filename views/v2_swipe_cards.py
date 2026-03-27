import streamlit as st
from core.state_manager import navigate_to
from core.recsys_engine import get_dynamic_tag_pairs, get_top_recommended_club

def render():
    st.title("🎴 发现你的热爱")
    
    # 1. 动态获取拔河卡片，并将其缓存进状态机，防止页面刷新时标签乱变
    if 'dynamic_pairs' not in st.session_state:
        st.session_state.dynamic_pairs = get_dynamic_tag_pairs(num_pairs=4)
        
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
        
    current_idx = st.session_state.swipe_index
    total_cards = len(st.session_state.dynamic_pairs)
    
    # 2. 核心流转逻辑：翻完动态生成的卡片后，触发推荐引擎
    if current_idx < total_cards:
        st.markdown(f"**匹配进度：{current_idx + 1} / {total_cards}**")
        st.markdown("凭借第一直觉，选择你更偏好的社团基因（Tag）：")
        
        pair = st.session_state.dynamic_pairs[current_idx]
        
        # 极致精简的 Tug of War 刻度
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
        # 3. 算法计算与拦截页面
        # ==========================================
        with st.spinner('🧠 正在融合你的画像特征与行为偏好...'):
            # 将 V1 的 profile 和 V2 的 history 全部喂给引擎
            best_club_id = get_top_recommended_club(
                st.session_state.user_profile, 
                st.session_state.swipe_history
            )
            
        st.session_state.current_club_view = best_club_id
        
        st.success("✨ 基于你的直觉与基础属性，AI 大脑已计算出最高得分社团！")
        st.info("侧边栏 AI 助手已就绪，正在为你生成个性化推荐理由 👇")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👀 立即查看专属推荐", type="primary", use_container_width=True):
                navigate_to('club_detail')
        with col2:
            if st.button("❌ 感觉不对，重洗标签", use_container_width=True):
                # 清除当前卡片池和历史，重新生成新的一批 Tags
                del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                st.session_state.swipe_history = []
                st.rerun()