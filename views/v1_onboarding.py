import streamlit as st
from core.state_manager import navigate_to

def render():
    """渲染破冰信息收集页"""
    st.title("👋 欢迎来到社团智能匹配平台")
    st.markdown("只需提供 3 个核心信息，AI 即可为你初始化专属的社团探索卡片！")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            mbti = st.selectbox("你的 MBTI 人格是？", 
                              ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "其他/暂时保密"])
            campus = st.selectbox("主要活动校区", 
                                ["北洋园校区", "卫津路校区", "其他"])
        with col2:
            time_commit = st.select_slider("每周愿意投入社团的时间", 
                                         options=["1-2小时 (边缘OB)", "3-5小时 (积极参与)", "6小时以上 (核心骨干)"])
        
        st.markdown("---")
        submitted = st.form_submit_button("生成我的专属匹配卡 🚀", type="primary", use_container_width=True)
        
        if submitted:
            # 数据写入状态机
            st.session_state.user_profile = {
                "mbti": mbti,
                "campus": campus,
                "time_commit": time_commit
            }
            navigate_to('swipe_cards')