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
        # 基本信息展示 (略，保持你之前的逻辑)
        st.subheader("📖 社团简介")
        st.write(club_info['detailed_description'])
        
        # 核心团队与架构 (略，保持你之前的逻辑)
        for dept in club_info.get('architecture', []):
            st.markdown(f"- **{dept['department']}**: {dept['role']}")

    with col_ai:
        st.subheader("🤖 AI 匹配助手")
        
        # ==========================================
        # 🚀 改进 1：冷启动检测与多样化话术
        # ==========================================
        swipe_history = st.session_state.get('swipe_history', [])
        cache_key = f"ai_reason_{club_id}"
        
        with st.chat_message("assistant"):
            if not swipe_history:
                # 情况 A：没有用户行为数据，拒绝分析并引导
                st.warning("🏮 哎呀，AI 助手目前还不了解你的偏好。")
                st.write("请先前往 **'AI 匹配'** 页面完成简单的潜意识测试，这样我才能为你提供精准的匹配分析哦！")
                if st.button("🎯 去测试一下", use_container_width=True):
                    navigate_to('swipe_cards')
            else:
                # 情况 B：有数据，正常分析
                if cache_key not in st.session_state:
                    # 随机选择一个话术模板前缀
                    templates = [
                        "🔍 **深度解析**：基于你在匹配测试中展现出的倾向，我发现...",
                        "💡 **匹配亮点**：之所以推荐这个社团，是因为你的潜意识告诉我们...",
                        "🎓 **学长视角**：结合你的性格画像，我认为这个社团非常适合你，理由是..."
                    ]
                    prefix = random.choice(templates)
                    
                    raw_reason = generate_match_reasoning(
                        user_profile=st.session_state.get('user_profile', {}),
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
            
            # ==========================================
            # 🚀 改进 2：打分与退出逻辑修复
            # ==========================================
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
                        # 此时触发询问是否结束
                        st.session_state.ask_to_finish = True
                        st.rerun()
                    else:
                        # 分数低则直接回滚，继续匹配
                        st.session_state.show_rating_area = False
                        navigate_to('swipe_cards')

                # 如果满足高分条件，显示退出询问
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