import json
import streamlit as st
import os
from core.state_manager import navigate_to
from core.recsys_engine import update_global_matrix_with_feedback
from core.mock_llm import generate_match_reasoning, stream_mock_response # 引入 AI 大脑组件

def load_club_data(club_id):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for club in data.get('clubs', []):
                if club['club_id'] == club_id:
                    return club
    except FileNotFoundError:
        st.error("未找到本地数据库 data/mock_clubs.json")
    return None

def render():
    club_id = st.session_state.get('current_club_view')
    if not club_id:
        st.warning("数据异常，即将返回首页...")
        navigate_to('swipe_cards')
        return

    club_info = load_club_data(club_id)
    if not club_info:
        st.error("未能加载社团信息。")
        return

    # --- 标题栏（加入社团客观评分） ---
    rating = club_info.get('club_rating', '暂无')
    st.title(f"🏆 {club_info['name']} ({rating} ⭐)")
    st.markdown(f"*{club_info['slogan']}*")
    st.caption(f"核心标签: {' · '.join(club_info['tags'])}")
    st.markdown("---")

    col_main, col_ai = st.columns([2, 1], gap="large")

    with col_main:
        # 【新增】基本信息模块展示 (成立时间、人数、频率)
        basic_info = club_info.get('basic_info', {})
        if basic_info:
            c1, c2, c3 = st.columns(3)
            c1.metric("成立年份", basic_info.get('established_year', '未知'))
            c2.metric("成员人数", basic_info.get('member_count', '未知'))
            c3.metric("活动频率", basic_info.get('activity_frequency', '未知'))
            st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        # 【新增】核心团队主席团展示
        leadership = club_info.get('leadership', [])
        if leadership:
            st.subheader("👨‍💻 核心团队")
            for leader in leadership:
                st.markdown(f"- **{leader['role']}**: {leader['name']}")
        
        st.subheader("⚙️ 组织架构")
        for dept in club_info.get('architecture', []):
            st.markdown(f"- **{dept['department']}**: {dept['role']}")
            
        st.subheader("📢 近期动态")
        for news in club_info.get('recent_news', []):
            with st.expander(f"{news['date']} - {news['title']}", expanded=True):
                st.write(news['content'])

        # 【新增】评价与口碑 (Mock)
        st.markdown("---")
        st.subheader("💬 历史评价与口碑")
        reviews = club_info.get('reviews', [])
        if not reviews:
            st.write("暂无历史评价。")
        else:
            for review in reviews:
                with st.container(border=True):
                    st.markdown(f"**{review['user']}** 给了 {review['rating']} 星  ·  *{review['date']}*")
                    st.write(review['comment'])

    with col_ai:
        st.subheader("🤖 AI 匹配分析")
        st.info("💡 **深入解析你的专属契合度...**")
        
        with st.chat_message("assistant"):
            # 1. 抽取当前用户的画像与偏好喂给 AI (使用 .get 防错，适应自然流量未填表的情况)
            llm_text = generate_match_reasoning(
                user_profile=st.session_state.get('user_profile', {}),
                swipe_history=st.session_state.get('swipe_history', []),
                club_info=club_info
            )
            
            # 2. 渲染打字机特效
            try:
                st.write_stream(stream_mock_response(llm_text))
            except AttributeError:
                st.write(llm_text)

        st.markdown("---")
        st.subheader("🎯 投递与操作")
        
        # ==========================================
        # 1. 投递按钮逻辑强化 (确保记录了已投递状态)
        # ==========================================
        if st.button("🚀 立即投递", type="primary", use_container_width=True):
            if 'applied_clubs' not in st.session_state:
                st.session_state.applied_clubs = []
            if club_id not in st.session_state.applied_clubs:
                st.session_state.applied_clubs.append(club_id)
            st.success("✅ 简历已一键发送至社团招新后台！(已同步至我的主页)")
            
        if st.button("⭐ 收藏该社团", use_container_width=True):
            st.toast("已加入收藏夹！")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 获取流量来源标识 (默认为 False)
        is_from_ai = st.session_state.get('from_ai_recommendation', False)

        if is_from_ai:
            # ==========================================
            # 场景 A: 从 AI 翻卡进入 -> 启动强制打分拦截与飞轮
            # ==========================================
            if 'show_rating' not in st.session_state:
                st.session_state.show_rating = False
            if 'ask_exit_loop' not in st.session_state:
                st.session_state.ask_exit_loop = False

            if st.session_state.ask_exit_loop:
                st.success("🎉 看来你已经成功投递了非常满意（≥4星）的社团！")
                st.info("是否结束本次心仪社团匹配，去广场看看其他内容？")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ 结束匹配，去逛广场", use_container_width=True):
                        st.session_state.show_rating = False
                        st.session_state.ask_exit_loop = False
                        st.session_state.current_club_view = None
                        navigate_to('home_dashboard') 
                with col_no:
                    if st.button("🔄 没看够，继续抽卡", use_container_width=True):
                        st.session_state.show_rating = False
                        st.session_state.ask_exit_loop = False
                        st.session_state.current_club_view = None
                        navigate_to('swipe_cards') 
                        
            elif not st.session_state.show_rating:
                if st.button("↩️ 再看看别的 (离开前需为 AI 打分)", use_container_width=True):
                    st.session_state.show_rating = True
                    
            else:
                st.warning("👇 请为本次 AI 匹配的精准度打分，帮助算法越算越准：")
                match_score = st.slider("1分(完全不搭) - 5分(完美契合)", 1, 5, 3)
                
                if st.button("提交反馈并返回", type="primary", use_container_width=True):
                    update_global_matrix_with_feedback(
                        club_id=club_id, match_score=match_score,
                        user_profile=st.session_state.get('user_profile', {}),
                        swipe_history=st.session_state.get('swipe_history', [])
                    )
                    has_applied = club_id in st.session_state.get('applied_clubs', [])
                    if match_score >= 4 and has_applied:
                        st.session_state.ask_exit_loop = True
                        st.rerun()
                    else:
                        st.session_state.show_rating = False
                        st.session_state.current_club_view = None
                        navigate_to('swipe_cards') 
        else:
            # ==========================================
            # 场景 B: 从广场自然进入 -> 取消打分，纯净浏览
            # ==========================================
            if st.button("⬅️ 返回刚才的页面", use_container_width=True):
                st.session_state.current_club_view = None
                # 返回发现广场
                navigate_to('home_dashboard')