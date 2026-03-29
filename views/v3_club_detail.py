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

    # --- 页面头部 ---
    st.title(f"🏆 {club_info['name']}")
    st.markdown(f"*{club_info['slogan']}*")
    st.markdown("---")

    col_main, col_ai = st.columns([2, 1], gap="large")

    with col_main:
        # 基本信息展示
        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        # 核心团队与架构
        for dept in club_info.get('architecture', []):
            st.markdown(f"- **{dept['department']}**: {dept['role']}")

    with col_ai:
        st.subheader("🤖 AI 匹配助手")
        
        # ==========================================
        # 🚀 改进：双层数据完整性拦截 (Profile + Swipe)
        # ==========================================
        user_profile = st.session_state.get('user_profile', {})
        mbti = user_profile.get('mbti', '--')
        campus = user_profile.get('campus', '--')
        time_commit = user_profile.get('time_commit', '--')
        
        # 判断基本 profile 是否缺失 (任何一个核心字段为默认或空)
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
                # 情况 A：基本 Profile 缺失，提示去完善档案
                st.warning("🏮 哎呀，你的基础破冰档案还不完整。")
                st.write("请先完善你的 **MBTI、主要活动校区、预期投入时间** 等基础信息，这样 AI 才能为你提供不悬浮的精准匹配分析！")
                if st.button("📝 立即完善档案", use_container_width=True):
                    # 巧妙联动：跳转到 V5 个人主页并直接激活编辑模式
                    st.session_state.edit_mode = True
                    navigate_to('profile')
                    
            elif not swipe_history:
                # 情况 B：有基本画像，但没有潜意识滑动数据，提示去翻卡
                st.warning("🏮 档案已就绪，但 AI 还需要了解你的直觉偏好。")
                st.write("请前往 **'AI 匹配'** 页面完成简单的潜意识测试，这样我才能为你生成专属分析报告哦！")
                if st.button("🎯 去测试一下", use_container_width=True):
                    navigate_to('swipe_cards')
                    
            else:
                # 情况 C：数据齐全，进行正常分析
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
                    st.write_stream(stream_mock_response(full_text))
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
                    # 更新全局矩阵
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