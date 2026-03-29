import streamlit as st
import json
import os
from core.state_manager import navigate_to

def load_clubs_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {club['club_id']: club for club in json.load(f).get('clubs', [])}
    except FileNotFoundError:
        return {}

def render():
    st.title("👤 我的主页")
    
    # ==========================================
    # 顶部全局导航栏
    # ==========================================
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 发现主页", use_container_width=True):
            navigate_to('home_dashboard')
    with col_nav2:
        if st.button("🎴 沉浸式 AI 匹配", use_container_width=True):
            navigate_to('swipe_cards')
    with col_nav3:
        st.button("👤 我的与投递", use_container_width=True, disabled=True)

    st.markdown("---")

    clubs_dict = load_clubs_data()

    # ==========================================
    # 模块 1：个人基础画像
    # ==========================================
    st.subheader("📝 我的画像")
    profile = st.session_state.get('user_profile', {})
    
    if not profile:
        st.warning("你还没有完成破冰信息填写。")
        if st.button("去完善信息"):
            navigate_to('onboarding')
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("MBTI", profile.get('mbti', '未设置'))
        col2.metric("每周可用时间", profile.get('time_commit', '未设置'))
        col3.metric("主要活动校区", profile.get('campus', '未设置'))

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 模块 2：投递与进度跟踪
    # ==========================================
    st.subheader("投递申请流程")
    applied_clubs = st.session_state.get('applied_clubs', [])
    
    if not applied_clubs:
        st.info("🎒 你目前还没有投递任何社团。快去广场或 AI 匹配找找心仪的组织吧！")
    else:
        for club_id in set(applied_clubs): # 使用 set 去重
            club = clubs_dict.get(club_id)
            if club:
                with st.container(border=True):
                    col_info, col_status = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{club['name']}**")
                        st.caption("已投递简历 | 正在等待社团负责人筛选")
                    with col_status:
                        st.button("查看详情", key=f"view_{club_id}", on_click=lambda c=club_id: (
                            st.session_state.update(
                                current_club_view=c,
                                from_ai_recommendation=False
                                ), 
                            navigate_to('club_detail')
                        ))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # 模块 3：算法反馈足迹
    # ==========================================
    st.subheader("我的打分足迹")
    feedbacks = st.session_state.get('match_feedbacks', [])
    if not feedbacks:
        st.write("暂无打分记录。")
    else:
        for fb in reversed(feedbacks[-5:]): # 只展示最近 5 条
            club_name = clubs_dict.get(fb['club_id'], {}).get('name', '未知社团')
            st.write(f"- 你为 **{club_name}** 的 AI 匹配推荐打了 **{fb['score']} 星**")