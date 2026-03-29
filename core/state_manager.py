import streamlit as st

def init_session_state():
    """初始化全局状态机"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'onboarding'
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
        
    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []
        
    if 'current_club_view' not in st.session_state:
        st.session_state.current_club_view = None
        
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0

def navigate_to(page_name):
    """全局路由跳转触发器"""
    st.session_state.current_page = page_name
    st.rerun()