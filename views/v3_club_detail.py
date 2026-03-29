import json
import streamlit as st
import os
import random
from core.state_manager import navigate_to
from core.recsys_engine import update_global_matrix_with_feedback
from core.mock_llm import generate_match_reasoning, stream_mock_response

def load_club_data(club_id):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for club in data.get('clubs', []):
                if club['club_id'] == club_id:
                    return club
    except FileNotFoundError:
        return None
    return None

def render():
    club_id = st.session_state.get('current_club_view')
    if not club_id:
        st.warning("数据异常，正在返回...")
        navigate_to('home_dashboard')
        return

    club_info = load_club_data(club_id)
    if not club_info:
        st.error("未能加载社团信息。")
        return

    # --- 页面头部 (恢复评分与标签) ---
    rating = club_info.get('club_rating', '暂无')
    st.title(f"🏆 {club_info['name']} ({rating} ⭐)")
    st.markdown(f"*{club_info['slogan']}*")
    tags_str = ' · '.join(club_info.get('tags', []))
    if tags_str:
        st.caption(f"核心标签: {tags_str}")
    st.markdown("---")

    col_main, col_ai = st.columns([2, 1], gap="large")

    with col_main:
        # ==========================================
        # 🔧 修复：全面恢复丢失的社团信息模块
        # ==========================================
        
        # 1. 基本信息模块展示 (成立时间、人数、频率)
        basic_info = club_info.get('basic_info', {})
        if basic_info:
            c1, c2, c3 = st.columns(3)
            c1.metric("成立年份", basic_info.get('established_year', '未知'))
            c2.metric("成员人数", basic_info.get('member_count', '未知'))
            c3.metric("活动频率", basic_info.get('activity_frequency', '未知'))
            st.markdown("<br>", unsafe_allow_html=True)

        # 2. 社团简介
        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        # 3. 核心团队主席团展示
        leadership = club_info.get('leadership', [])
        if leadership:
            st.subheader("👨‍💻 核心团队")
            for leader in leadership:
                st.markdown(f"- **{leader['role']}**: {leader['name']}")
        
        # 4. 组织架构
        st.subheader("⚙️ 组织架构")
        for dept in club_info.get('architecture', []):
            st.markdown(f"- **{dept['department']}**: {dept['role']}")
            
        # 5. 近期动态 (折叠面板)
        recent_news = club_info.get('recent_news', [])
        if recent_news:
            st.subheader("📢 近期动态")
            for news in recent_news:
                with st.expander(f"{news['date']} - {news['title']}", expanded=True):
                    st.write(news['content'])

        # 6. 评价与口碑
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
        st.subheader("🤖 AI 匹配助手")
        
        # ==========================================
        # 🚀 保持不变：双层数据完整性拦截 (Profile + Swipe)
        # ==========================================
        user_profile = st.session_state.get('user_profile', {})
        mbti = user_profile.get('mbti', '--')
        campus = user_profile.get('campus', '--')
        time_commit = user_profile.get('time_commit', '--')
        
        is_profile_missing = (
            not user_profile or 
            mbti in ["--", "", None, "保密", "未知", "其他/暂时保密"] or 
            campus in ["--", "", None] or 
            time_commit in ["--", "", None]
        )
        
        swipe_history = st.session_state.get('swipe_history', [])
        cache_key = f"ai_reason_{club_id}"
        
        with st.chat_message("assistant"):
            if is_profile_missing:
                st.warning("🏮 哎呀，你的基础破冰档案还不完整。")
                st.write("请先完善你的 **MBTI、主要活动校区、预期投入时间** 等基础信息，这样 AI 才能为你提供不悬浮的精准匹配分析！")
                if st.button("📝 立即完善档案", use_container_width=True):
                    st.session_state.edit_mode = True
                    navigate_to('profile')
                    
            elif not swipe_history:
                st.warning("🏮 档案已就绪，但 AI 还需要了解你的直觉偏好。")
                st.write("请前往 **'AI 匹配'** 页面完成简单的潜意识测试，这样我才能为你生成专属分析报告哦！")
                if st.button("🎯 去测试一下", use_container_width=True):
                    navigate_to('swipe_cards')
                    
            else:
                if cache_key not in st.session_state:
                    templates = [
                        "🔍 **深度解析**：基于你在匹配测试中展现出的倾向，我发现...",
                        "💡 **匹配亮点**：之所以推荐这个社团，是因为你的潜意识告诉我们...",
                        "🎓 **学长视角**：结合你的性格画像，我认为这个社团非常适合你，理由是..."
                    ]
                    prefix = random.choice(templates)
                    
                    raw_reason = generate_match_reasoning(
                        user_profile=user_profile,
                        swipe_history=swipe_history,
                        club_info=club_info
                    )
                    full_text = f"{prefix}\n\n{raw_reason}"
                    st.session_state[cache_key] = full_text
                    try:
                        st.write_stream(stream_mock_response(full_text))
                    except AttributeError:
                        st.write(full_text)
                else:
                    st.write(st.session_state[cache_key])

        st.markdown("---")
        st.subheader("🎯 投递与反馈")
        
        if st.button("🚀 立即投递", type="primary", use_container_width=True):
            if 'applied_clubs' not in st.session_state:
                st.session_state.applied_clubs = []
            if club_id not in st.session_state.applied_clubs:
                st.session_state.applied_clubs.append(club_id)
            st.success("✅ 简历已投递！")
            
        is_from_ai = st.session_state.get('from_ai_recommendation', False)

        if is_from_ai:
            if 'show_rating_area' not in st.session_state:
                st.session_state.show_rating_area = False
            
            if not st.session_state.show_rating_area:
                if st.button("↩️ 再看看别的", use_container_width=True):
                    st.session_state.show_rating_area = True
                    st.rerun()
            else:
                st.info("💡 评价本次匹配，帮助 AI 进化：")
                score = st.slider("精准度打分", 1, 5, 4)
                
                if st.button("提交反馈", type="primary", use_container_width=True):
                    update_global_matrix_with_feedback(club_id, score, st.session_state.get('user_profile', {}), swipe_history)
                    
                    if score >= 4:
                        st.session_state.ask_to_finish = True
                        st.rerun()
                    else:
                        st.session_state.show_rating_area = False
                        navigate_to('swipe_cards')

                if st.session_state.get('ask_to_finish'):
                    st.success("🎉 看来 AI 已经帮你找到了心仪的目标！")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ 结束测试", use_container_width=True):
                            st.session_state.show_rating_area = False
                            st.session_state.ask_to_finish = False
                            navigate_to('home_dashboard')
                    with c2:
                        if st.button("🔄 继续探索", use_container_width=True):
                            st.session_state.show_rating_area = False
                            st.session_state.ask_to_finish = False
                            navigate_to('swipe_cards')
        else:
            if st.button("⬅️ 返回广场", use_container_width=True):
                navigate_to('home_dashboard')