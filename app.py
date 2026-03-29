import streamlit as st
from core.state_manager import init_session_state
from views import v1_onboarding
from views import v2_swipe_cards
from views import v3_club_detail
from views import v4_home_dashboard
from views import v5_profile

# 1. 全局配置
st.set_page_config(
    page_title="翻得-Find Your Club",
    page_icon="🎯",
    layout="centered"
)

# 2. 唤醒状态机
init_session_state()

# 3. 路由分发中心 (Router)
if st.session_state.current_page == 'onboarding':
    v1_onboarding.render()
elif st.session_state.current_page == 'swipe_cards':
    v2_swipe_cards.render()
elif st.session_state.current_page == 'club_detail':
    v3_club_detail.render()
elif st.session_state.current_page == 'home_dashboard':
    v4_home_dashboard.render()
elif st.session_state.current_page == 'profile':
    v5_profile.render()