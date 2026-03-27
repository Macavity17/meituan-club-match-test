import streamlit as st

def init_session_state():
    """初始化全局状态机"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'onboarding' # 默认入口页
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}           # 用户破冰信息
        
    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []          # 用户的滑动打分序列
        
    if 'current_club_view' not in st.session_state:
        st.session_state.current_club_view = None    # 当前正在查看的社团详情

def navigate_to(page_name):
    """全局路由跳转触发器"""
    st.session_state.current_page = page_name
    st.rerun()