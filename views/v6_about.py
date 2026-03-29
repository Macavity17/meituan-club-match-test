import streamlit as st
import os
from core.state_manager import navigate_to

def render():
    st.title("ℹ️ 关于项目")
    
    # 顶部的四栏全局导航
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 发现主页", use_container_width=True): navigate_to('home_dashboard')
    with col2:
        if st.button("🎴 AI 匹配", use_container_width=True): navigate_to('swipe_cards')
    with col3:
        if st.button("👤 我的投递", use_container_width=True): navigate_to('profile')
    with col4:
        st.button("ℹ️ 关于", use_container_width=True, disabled=True)
    st.markdown("---")

    # 动态读取并渲染 README.md
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        st.markdown(readme_content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("未找到 README.md 文件，请确保其位于项目根目录。")