import json
import streamlit as st
import os
from core.state_manager import navigate_to
from core.recsys_engine import update_global_matrix_with_feedback  # 引入飞轮更新接口

def load_club_data(club_id):
    """从本地读取 JSON 模拟数据库"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for club in data.get('clubs', []):
                if club['club_id'] == club_id:
                    return club
    except FileNotFoundError:
        st.error("未找到本地数据库 data/mock_clubs.json")
    return None

def render():
    club_id = st.session_state.get('current_club_view')
    if not club_id:
        st.warning("数据异常，即将返回首页...")
        navigate_to('swipe_cards')
        return

    club_info = load_club_data(club_id)
    if not club_info:
        st.error("未能加载社团信息。")
        return

    # 顶部头图与 Slogan
    st.title(f"🏆 {club_info['name']}")
    st.markdown(f"*{club_info['slogan']}*")
    st.caption(f"核心标签: {' · '.join(club_info['tags'])}")
    st.markdown("---")

    # 左右分栏设计：左侧详细信息，右侧 AI 助手
    col_main, col_ai = st.columns([2, 1], gap="large")

    with col_main:
        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        st.subheader("⚙️ 组织架构")
        for dept in club_info['architecture']:
            st.markdown(f"- **{dept['department']}**: {dept['role']}")
            
        st.subheader("📢 近期动态")
        for news in club_info['recent_news']:
            with st.expander(f"{news['date']} - {news['title']}", expanded=True):
                st.write(news['content'])

    with col_ai:
        st.subheader("🤖 AI 匹配分析")
        st.info("💡 **分析助手正在运行...**")
        
        # 提取用户的基础画像用于假 LLM 的 Context (后续将接入 core/mock_llm.py)
        user_mbti = st.session_state.user_profile.get('mbti', '未知')
        user_time = st.session_state.user_profile.get('time_commit', '未知')
        
        with st.chat_message("assistant"):
            st.write(f"结合你是 **{user_mbti}** 人格，并且每周有 **{user_time}** 的空闲时间，我强烈推荐你关注他们的【{club_info['architecture'][0]['department']}】。")
            st.write("根据你刚才在拔河卡片中的偏向，这个社团的氛围非常适合你目前的诉求！")

        st.markdown("---")
        st.subheader("🎯 投递与操作")
        
        if st.button("🚀 立即投递", type="primary", use_container_width=True):
            st.success("✅ 简历已一键发送至社团招新后台！")
            
        if st.button("⭐ 收藏该社团", use_container_width=True):
            st.toast("已加入收藏夹！")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # 强制打分拦截与飞轮反馈链路
        # ==========================================
        if 'show_rating' not in st.session_state:
            st.session_state.show_rating = False

        if not st.session_state.show_rating:
            if st.button("↩️ 再看看别的 (离开前需打分)", use_container_width=True):
                st.session_state.show_rating = True
                st.rerun()
        else:
            st.warning("👇 请为本次匹配的精准度打分，这将帮助 AI 优化后续推荐：")
            match_score = st.slider("1分(完全不搭) - 5分(完美契合)", 1, 5, 3)
            
            if st.button("提交反馈并返回", type="primary", use_container_width=True):
                # 1. 触发推荐引擎的全局统矩阵更新（数据飞轮闭环）
                update_global_matrix_with_feedback(
                    club_id=club_id,
                    match_score=match_score,
                    user_profile=st.session_state.user_profile,
                    swipe_history=st.session_state.swipe_history
                )
                
                # 2. 仅为 Demo 演示记录，将打分压入本地状态
                if 'match_feedbacks' not in st.session_state:
                    st.session_state.match_feedbacks = []
                st.session_state.match_feedbacks.append({
                    "club_id": club_id,
                    "score": match_score
                })
                
                # 3. 清除当前视图状态并返回拔河翻卡页
                st.session_state.show_rating = False
                st.session_state.current_club_view = None
                navigate_to('swipe_cards')