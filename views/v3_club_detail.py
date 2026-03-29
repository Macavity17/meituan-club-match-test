import json
import streamlit as st
import os
from core.state_manager import navigate_to
from core.recsys_engine import update_global_matrix_with_feedback
from core.mock_llm import generate_match_reasoning, stream_mock_response

def load_club_data(club_id):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for club in data.get('clubs', []):
                if club['club_id'] == club_id:
                    return club
    except FileNotFoundError:
        return None
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

    # --- 标题栏 ---
    rating = club_info.get('club_rating', '暂无')
    st.title(f"🏆 {club_info['name']} ({rating} ⭐)")
    st.markdown(f"*{club_info['slogan']}*")
    st.markdown("---")

    col_main, col_ai = st.columns([2, 1], gap="large")

    with col_main:
        # 基本信息模块
        basic_info = club_info.get('basic_info', {})
        if basic_info:
            c1, c2, c3 = st.columns(3)
            c1.metric("成立年份", basic_info.get('established_year', '未知'))
            c2.metric("成员人数", basic_info.get('member_count', '未知'))
            c3.metric("活动频率", basic_info.get('activity_frequency', '未知'))
            st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        # 核心团队
        leadership = club_info.get('leadership', [])
        if leadership:
            st.subheader("👨‍💻 核心团队")
            for leader in leadership:
                st.markdown(f"- **{leader['role']}**: {leader['name']}")
        
        st.subheader("⚙️ 组织架构")
        for dept in club_info.get('architecture', []):
            st.markdown(f"- **{dept['department']}**: {dept['role']}")

    with col_ai:
        st.subheader("🤖 AI 匹配分析")
        
        # ==========================================
        # 🚀 修复：AI 理由缓存机制 (防止重绘抖动)
        # ==========================================
        cache_key = f"ai_reason_{club_id}"
        
        with st.chat_message("assistant"):
            if cache_key not in st.session_state:
                # 第一次进入：执行打字机特效
                llm_text = generate_match_reasoning(
                    user_profile=st.session_state.get('user_profile', {}),
                    swipe_history=st.session_state.get('swipe_history', []),
                    club_info=club_info
                )
                # 存入缓存
                st.session_state[cache_key] = llm_text
                try:
                    st.write_stream(stream_mock_response(llm_text))
                except AttributeError:
                    st.write(llm_text)
            else:
                # 之后的任何操作（如点按钮）：直接显示缓存内容，不再重绘动画
                st.write(st.session_state[cache_key])

        st.markdown("---")
        st.subheader("🎯 投递与操作")
        
        if st.button("🚀 立即投递", type="primary", use_container_width=True):
            if 'applied_clubs' not in st.session_state:
                st.session_state.applied_clubs = []
            if club_id not in st.session_state.applied_clubs:
                st.session_state.applied_clubs.append(club_id)
            st.success("✅ 简历已投递！")
            
        is_from_ai = st.session_state.get('from_ai_recommendation', False)

        if is_from_ai:
            if 'show_rating' not in st.session_state:
                st.session_state.show_rating = False
            
            # 点击按钮立即改变状态并重绘，配合缓存机制，现在反应极快
            if not st.session_state.show_rating:
                if st.button("↩️ 再看看别的 (离开前请评价)", use_container_width=True):
                    st.session_state.show_rating = True
                    st.rerun() # 强制立即重绘以显示打分组件
            else:
                st.warning("👇 请为 AI 匹配精准度打分：")
                match_score = st.slider("匹配度 (1-5)", 1, 5, 3)
                
                if st.button("提交反馈并返回", type="primary", use_container_width=True):
                    # 负反馈黑名单逻辑
                    if match_score <= 2:
                        if 'disliked_clubs' not in st.session_state:
                            st.session_state.disliked_clubs = set()
                        st.session_state.disliked_clubs.add(club_id)
                    
                    update_global_matrix_with_feedback(
                        club_id=club_id, match_score=match_score,
                        user_profile=st.session_state.get('user_profile', {}),
                        swipe_history=st.session_state.get('swipe_history', [])
                    )
                    # 重置详情页状态，清理缓存，返回翻卡
                    st.session_state.show_rating = False
                    st.session_state.current_club_view = None
                    navigate_to('swipe_cards')
        else:
            if st.button("⬅️ 返回发现广场", use_container_width=True):
                st.session_state.current_club_view = None
                navigate_to('home_dashboard')