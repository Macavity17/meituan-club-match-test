import streamlit as st
import json
import os
from core.state_manager import navigate_to

def load_clubs_data():
    """从本地读取所有社团数据"""
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f).get('clubs', [])
    except FileNotFoundError:
        st.error("未找到本地数据库 data/mock_clubs.json")
    return []

def get_all_news(clubs):
    """聚合全站所有社团的近期新闻，并按日期排序 (Mock)"""
    all_news = []
    for club in clubs:
        for news in club.get('recent_news', []):
            # 将社团名称注入到新闻源中
            news_with_source = news.copy()
            news_with_source['club_name'] = club['name']
            news_with_source['club_id'] = club['club_id']
            all_news.append(news_with_source)
    # 按日期倒序 (假设格式均为 YYYY-MM-DD)
    all_news.sort(key=lambda x: x['date'], reverse=True)
    return all_news

def render():
    st.title("🏠 社团发现广场")
    
    # 【新增】顶部小字仓库链接
    st.caption("🔗 [访问 GitHub 仓库获取源码](https://https://github.com/Macavity17/meituan-club-match-test)")
    
    # ==========================================
    # 顶部全局导航栏 (Mock 切换)
    # ==========================================
    # 【修改】扩充为 4 栏导航栏
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    with col_nav1:
        st.button("🏠 发现主页", use_container_width=True, disabled=True)
    with col_nav2:
        if st.button("🎴 沉浸式 AI 匹配", use_container_width=True):
            navigate_to('swipe_cards')
    with col_nav3:
        if st.button("👤 我的与投递", use_container_width=True):
            navigate_to('profile')
    with col_nav4:
        if st.button("ℹ️ 关于", use_container_width=True):
            navigate_to('about')

    st.markdown("---")

    # ==========================================
    # 核心引流位：AI 智能匹配入口
    # ==========================================
    st.info("✨ 挑花了眼？不知道自己适合什么？让 AI 算法结合你的潜意识，帮你快速定位！")
    if st.button("🚀 开启智能匹配 (Tug of War)", type="primary", use_container_width=True):
        navigate_to('swipe_cards')
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    clubs = load_clubs_data()
    if not clubs:
        return

    # ==========================================
    # 双轨内容流：热门社团 & 新鲜事瀑布流
    # ==========================================
    tab_hot, tab_news = st.tabs(["🔥 热门社团推荐", "📢 全站新鲜事"])

    # --- Tab 1: 热门社团展示 (Grid 布局) ---
    with tab_hot:
        st.markdown("<br>", unsafe_allow_html=True)
        # 用两列排布社团卡片
        col1, col2 = st.columns(2)
        for i, club in enumerate(clubs):
            # 交替放置在左右列
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    st.subheader(club['name'])
                    st.caption(f"📍 {' · '.join(club['tags'][:2])}") # 只展示前两个 tag 防折行
                    st.write(club['slogan'])
                    if st.button(f"查看详情", key=f"btn_{club['club_id']}", use_container_width=True):
                        st.session_state.current_club_view = club['club_id']
                        st.session_state.from_ai_recommendation = False
                        navigate_to('club_detail')

    # --- Tab 2: 新鲜事瀑布流 ---
    with tab_news:
        st.markdown("<br>", unsafe_allow_html=True)
        all_news = get_all_news(clubs)
        if not all_news:
            st.write("暂无最新鲜事")
        else:
            for news in all_news:
                with st.container(border=True):
                    st.markdown(f"**{news['title']}**")
                    st.caption(f"来源: {news['club_name']} | 发布于 {news['date']}")
                    st.write(news['content'])
                    # 快捷跳转至发布该新闻的社团
                    if st.button("去社团看看", key=f"news_btn_{news['title']}_{news['club_id']}"):
                         st.session_state.current_club_view = news['club_id']
                         st.session_state.from_ai_recommendation = False
                         navigate_to('club_detail')