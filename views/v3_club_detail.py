import json
import streamlit as st
import os
from core.state_manager import navigate_to
from core.recsys_engine import update_global_matrix_with_feedback
from core.mock_llm import generate_match_reasoning, stream_mock_response # 引入 AI 大脑组件

def load_club_data(club_id):
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

    st.title(f"🏆 {club_info['name']}")
    st.markdown(f"*{club_info['slogan']}*")
    st.caption(f"核心标签: {' · '.join(club_info['tags'])}")
    st.markdown("---")

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
        st.info("💡 **深入解析你的专属契合度...**")
        
        with st.chat_message("assistant"):
            # 1. 抽取当前用户的画像与偏好喂给 AI
            llm_text = generate_match_reasoning(
                user_profile=st.session_state.user_profile,
                swipe_history=st.session_state.swipe_history,
                club_info=club_info
            )
            
            # 2. 渲染打字机特效
            try:
                st.write_stream(stream_mock_response(llm_text))
            except AttributeError:
                st.write(llm_text)

        st.markdown("---")
        st.subheader("🎯 投递与操作")
        
        # ==========================================
        # 1. 投递按钮逻辑强化 (确保记录了已投递状态)
        # ==========================================
        if st.button("🚀 立即投递", type="primary", use_container_width=True):
            if 'applied_clubs' not in st.session_state:
                st.session_state.applied_clubs = []
            if club_id not in st.session_state.applied_clubs:
                st.session_state.applied_clubs.append(club_id)
            st.success("✅ 简历已一键发送至社团招新后台！(已同步至我的主页)")
            
        if st.button("⭐ 收藏该社团", use_container_width=True):
            st.toast("已加入收藏夹！")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # 2. 强制打分拦截与聪明的循环跳出逻辑
        # ==========================================
        if 'show_rating' not in st.session_state:
            st.session_state.show_rating = False
        if 'ask_exit_loop' not in st.session_state:
            st.session_state.ask_exit_loop = False # 新增拦截状态

        # --- 场景 A：触发了询问弹窗 ---
        if st.session_state.ask_exit_loop:
            st.success("🎉 看来你已经成功投递了非常满意（≥4星）的社团！")
            st.info("是否结束本次心仪社团匹配，去广场看看其他内容？")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✅ 结束匹配，去逛广场", use_container_width=True):
                    st.session_state.show_rating = False
                    st.session_state.ask_exit_loop = False
                    st.session_state.current_club_view = None
                    navigate_to('home_dashboard') # 结束循环，去 V4
            with col_no:
                if st.button("🔄 没看够，继续抽卡", use_container_width=True):
                    st.session_state.show_rating = False
                    st.session_state.ask_exit_loop = False
                    st.session_state.current_club_view = None
                    navigate_to('swipe_cards') # 继续无尽循环，回 V2
                    
        # --- 场景 B：正常的强制打分拦截 ---
        elif not st.session_state.show_rating:
            if st.button("↩️ 再看看别的 (离开前需打分)", use_container_width=True):
                st.session_state.show_rating = True
                st.rerun()
                
        # --- 场景 C：提交打分并判断去向 ---
        else:
            st.warning("👇 请为本次匹配的精准度打分，这将帮助 AI 优化后续推荐：")
            match_score = st.slider("1分(完全不搭) - 5分(完美契合)", 1, 5, 3)
            
            if st.button("提交反馈并返回", type="primary", use_container_width=True):
                # 触发飞轮数据回流
                update_global_matrix_with_feedback(
                    club_id=club_id,
                    match_score=match_score,
                    user_profile=st.session_state.user_profile,
                    swipe_history=st.session_state.swipe_history
                )
                
                # 判断是否满足“跳出循环”的条件：打分 >= 4 且 已经投递了该社团
                has_applied = club_id in st.session_state.get('applied_clubs', [])
                
                if match_score >= 4 and has_applied:
                    # 满足条件，触发弹窗询问 (场景A)
                    st.session_state.ask_exit_loop = True
                    st.rerun()
                else:
                    # 不满足条件（例如只打了3分，或者没投递），强制继续循环！
                    st.session_state.show_rating = False
                    st.session_state.current_club_view = None
                    navigate_to('swipe_cards') # 核心修复：无条件滚回 V2 继续抽卡