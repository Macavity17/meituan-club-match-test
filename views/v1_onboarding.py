import streamlit as st
from core.state_manager import navigate_to

def render():
    """渲染破冰信息收集页"""
    st.title("翻得-Find My Club\n💛 探索校园热爱 | AI 匹配引擎")
    st.markdown("告别「百团大战」的信息过载。只需提供 3 个核心破冰标签，底层推荐算法将为你初始化专属的探索飞轮！")
    
    # 定义空选项常量
    EMPTY_CHOICE = "--- 请选择 ---"
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            mbti = st.selectbox("🧬 你的 MBTI 精神图腾是？ *(必填)*", 
                              [EMPTY_CHOICE, "INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "其他/暂时保密"],
                              index=0)
            campus = st.selectbox("📍 主要活动坐标 *(必填)*", 
                                [EMPTY_CHOICE, "北洋园校区", "卫津路校区", "其他"],
                                index=0)
        with col2:
            # 将滑块改为下拉框，以支持“空状态”的必填校验
            time_commit = st.selectbox("⏱️ 预期每周投入精力 *(必填)*", 
                                     [EMPTY_CHOICE, "1-2小时 (边缘OB)", "3-5小时 (积极参与)", "6小时以上 (核心骨干)"],
                                     index=0)
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 启动匹配算法，遇见心仪社团", type="primary", use_container_width=True)
        
        if submitted:
            # 🚨 强校验逻辑：如果有任何一项还是默认的占位符，拒绝放行
            if EMPTY_CHOICE in [mbti, campus, time_commit]:
                st.error("🚨 启动失败：请完善所有 3 项必填信息，以便 AI 引擎能精准识别你的特质！")
            else:
                # 校验通过，写入状态机并跳转
                st.session_state.user_profile = {
                    "mbti": mbti,
                    "campus": campus,
                    "time_commit": time_commit
                }
                navigate_to('swipe_cards')

    st.markdown("<br>", unsafe_allow_html=True)
    # 广场按钮依然在 form 外面，任何时候都可以点击跳过
    if st.button("👀 暂时保密，先去社团广场「吃瓜」", use_container_width=True):
        navigate_to('home_dashboard')