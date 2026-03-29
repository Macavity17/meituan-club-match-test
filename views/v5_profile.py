import streamlit as st
import json
import os
from core.state_manager import navigate_to

def load_clubs_data():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_clubs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {club['club_id']: club for club in json.load(f).get('clubs', [])}
    except FileNotFoundError:
        return {}

def render():
    st.title("👤 我的主页")
    
    # ==========================================
    # 顶部 4 栏导航
    # ==========================================
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    with col_nav1:
        if st.button("🏠 发现主页", use_container_width=True):
            navigate_to('home_dashboard')
    with col_nav2:
        if st.button("🎴 AI 匹配", use_container_width=True):
            navigate_to('swipe_cards')
    with col_nav3:
        st.button("👤 我的主页", use_container_width=True, disabled=True)
    with col_nav4:
        if st.button("ℹ️ 关于", use_container_width=True):
            navigate_to('about')

    st.markdown("---")

    clubs_dict = load_clubs_data()

    # ==========================================
    # 模块 1：大 Profile 个人档案
    # ==========================================
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    profile = st.session_state.user_profile
    
    # 🎯 【全部置空的默认值】
    defaults = {
        "name": "",
        "gender": "保密",
        "enrollment_year": "2024", 
        "mbti": profile.get("mbti", "保密"), 
        "campus": profile.get("campus", "其他"), 
        "time_commit": profile.get("time_commit", "1-2小时"),
        "college": "",
        "major": "",
        "bio": ""
    }
    
    for k, v in defaults.items():
        if k not in profile or not profile[k]:
            profile[k] = v

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # 判断是否为初始未填写状态
    is_empty = not profile.get("name")

    st.subheader("📝 个人档案")
    with st.container(border=True):
        if st.session_state.edit_mode:
            # --- ✏️ 编辑模式 ---
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("姓名", value=profile.get("name", ""), placeholder="请输入真实姓名")
                
                year_options = ["2022", "2023", "2024", "2025", "2026"]
                year_idx = year_options.index(profile["enrollment_year"]) if profile["enrollment_year"] in year_options else 2
                new_year = st.selectbox("入学年份", year_options, index=year_idx)
                
            with c2:
                gender_options = ["男", "女", "其他", "保密"]
                gender_idx = gender_options.index(profile["gender"]) if profile["gender"] in gender_options else 3
                new_gender = st.selectbox("性别", gender_options, index=gender_idx)
            
            st.markdown("---")
            c3, c4, c5 = st.columns(3)
            with c3:
                mbti_opts = ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "保密"]
                mbti_idx = mbti_opts.index(profile["mbti"]) if profile["mbti"] in mbti_opts else 8
                new_mbti = st.selectbox("MBTI", mbti_opts, index=mbti_idx)
            with c4:
                campus_opts = ["北洋园校区", "卫津路校区", "其他"]
                campus_idx = campus_opts.index(profile["campus"]) if profile["campus"] in campus_opts else 2
                new_campus = st.selectbox("校区", campus_opts, index=campus_idx)
            with c5:
                time_opts = ["1-2小时", "3-5小时", "6小时以上"]
                time_idx = time_opts.index(profile["time_commit"]) if profile["time_commit"] in time_opts else 0
                new_time = st.selectbox("投入时间", time_opts, index=time_idx)

            st.markdown("---")
            c6, c7 = st.columns(2)
            with c6:
                new_college = st.text_input("学院", value=profile.get("college", ""), placeholder="例如：天津大学")
            with c7:
                new_major = st.text_input("专业", value=profile.get("major", ""), placeholder="例如：管理科学与工程")

            new_bio = st.text_area("简介", value=profile.get("bio", ""), height=100, placeholder="简单介绍一下自己，让社团更好地认识你...")
            
            if st.button("💾 保存更改", type="primary", use_container_width=True):
                st.session_state.user_profile.update({
                    "name": new_name, "gender": new_gender, "enrollment_year": new_year,
                    "mbti": new_mbti, "campus": new_campus, "time_commit": new_time,
                    "college": new_college, "major": new_major, "bio": new_bio
                })
                st.session_state.edit_mode = False
                st.rerun()

        elif is_empty:
            # --- 💡 引导模式 ---
            st.info("👋 你的档案目前还是初始状态。完善后 AI 匹配将更加精准！")
            if st.button("✨ 立即完善个人档案", type="primary", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

        else:
            # --- 📖 阅览模式 ---
            col_t, col_b = st.columns([4, 1])
            with col_t:
                st.markdown(f"### {profile.get('name', '未知姓名')}  `{profile.get('gender', '保密')}`")
            with col_b:
                if st.button("✏️ 编辑", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()
            
            college_display = profile.get('college') if profile.get('college') else "未填写学院"
            major_display = profile.get('major') if profile.get('major') else "未填写专业"
            
            st.markdown(f"🎓 **{college_display}** · {major_display} ({profile.get('enrollment_year', '未知')}级)")
            st.markdown(f"🏷️ `{profile.get('mbti', '保密')}` · `{profile.get('campus', '其他')}` · `{profile.get('time_commit', '未知')}`")
            
            bio_display = profile.get('bio') if profile.get('bio') else "暂无简介"
            st.info(bio_display)

    # ==========================================
    # 模块 2：投递记录
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📬 投递进度")
    applied_clubs = st.session_state.get('applied_clubs', [])
    
    if not applied_clubs:
        st.info("🎒 目前还没有投递记录。")
    else:
        for club_id in list(dict.fromkeys(applied_clubs)): 
            club = clubs_dict.get(club_id)
            if club:
                with st.container(border=True):
                    col_info, col_status = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{club['name']}**")
                        st.caption("状态：已投递简历 · 等待负责人筛选")
                    with col_status:
                        if st.button("查看详情", key=f"v_{club_id}", use_container_width=True):
                            st.session_state.current_club_view = club_id
                            st.session_state.from_ai_recommendation = False
                            navigate_to('club_detail')