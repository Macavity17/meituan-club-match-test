import streamlit as st
from core.state_manager import init_session_state
from views import v1_onboarding

# 注意：生产环境中，其他视图写好后在这里 import 即可
# from views import v2_swipe_cards, v3_club_detail, v4_home_dashboard, v5_profile

# 1. 全局配置
st.set_page_config(
    page_title="社团招新智能匹配平台",
    page_icon="🎯",
    layout="centered"
)

# 2. 唤醒状态机
init_session_state()

# 3. 路由分发中心 (Router)
if st.session_state.current_page == 'onboarding':
    v1_onboarding.render()

# 后续开发完成后，按此结构解开注释即可：
elif st.session_state.current_page == 'swipe_cards':
    v2_swipe_cards.render()
# elif st.session_state.current_page == 'club_detail':
#     v3_club_detail.render()
# elif st.session_state.current_page == 'home_dashboard':
#     v4_home_dashboard.render()
# elif st.session_state.current_page == 'profile':
#     v5_profile.render()