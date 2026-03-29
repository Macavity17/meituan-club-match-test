import streamlit as st
from core.state_manager import navigate_to

def render():
    """渲染破冰信息收集页"""
    # 强化品牌定位与产品概念
    st.title("💛 探索校园热爱 | AI 匹配引擎")
    st.markdown("告别「百团大战」的信息过载。只需提供 3 个核心破冰标签，底层推荐算法将为你初始化专属的探索飞轮！")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            # 增加字段的趣味性与代入感
            mbti = st.selectbox("🧬 你的 MBTI 精神图腾是？", 
                              ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "其他/暂时保密"])
            campus = st.selectbox("📍 主要活动坐标", 
                                ["北洋园校区", "卫津路校区", "其他"])
        with col2:
            time_commit = st.select_slider("⏱️ 预期每周投入精力", 
                                         options=["1-2小时 (边缘OB)", "3-5小时 (积极参与)", "6小时以上 (核心骨干)"])
        
        st.markdown("---")
        # 按钮文案更具行动号召力 (Call to Action)
        submitted = st.form_submit_button("🚀 启动匹配算法，遇见心仪社团", type="primary", use_container_width=True)
        
        if submitted:
            # 数据写入状态机[cite: 10]
            st.session_state.user_profile = {
                "mbti": mbti,
                "campus": campus,
                "time_commit": time_commit
            }
            navigate_to('swipe_cards')

    st.markdown("<br>", unsafe_allow_html=True)
    # 弱化跳过按钮，用“吃瓜”等轻松词汇拉近距离
    if st.button("👀 暂时保密，先去社团广场「吃瓜」", use_container_width=True):
        navigate_to('home_dashboard')