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
    
    # 🎯 【完全保留你的原版默认值字典，一字未动】
    defaults = {
        "name": "--",
        "gender": "--",
        "enrollment_year": "--",
        "mbti": profile.get("mbti", "--"),
        "campus": profile.get("campus", "--"),
        "time_commit": profile.get("time_commit", "--"),
        "college": "天津大学",
        "major": "管理科学与工程",
        "bio": "来自青岛，对资产配置和AI大模型有浓厚兴趣。平时喜欢健身和看展。目前正在准备关于员工对AI幻觉容忍度的毕业论文。"
    }
    
    for k, v in defaults.items():
        if k not in profile or not profile[k]:
            profile[k] = v

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # 💡 【仅新增这一行】：判断是否为初始 "--" 状态
    is_empty = profile.get("name") == "--"

    st.subheader("📝 个人档案")
    with st.container(border=True):
        if st.session_state.edit_mode:
            # --- ✏️ 编辑模式 (完全保留你的原版代码) ---
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("姓名", value=profile["name"])
                new_year = st.selectbox("入学年份", ["2022", "2023", "2024", "2025", "2026"], index=2)
            with c2:
                new_gender = st.selectbox("性别", ["男", "女", "其他", "保密"], index=0)
            
            st.markdown("---")
            c3, c4, c5 = st.columns(3)
            with c3:
                new_mbti = st.selectbox("MBTI", ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "保密"], index=1)
            with c4:
                new_campus = st.selectbox("校区", ["北洋园校区", "卫津路校区", "其他"], index=1)
            with c5:
                new_time = st.selectbox("投入时间", ["1-2小时", "3-5小时", "6小时以上"], index=1)

            st.markdown("---")
            c6, c7 = st.columns(2)
            with c6:
                new_college = st.text_input("学院", value=profile["college"])
            with c7:
                new_major = st.text_input("专业", value=profile["major"])

            new_bio = st.text_area("简介", value=profile["bio"], height=100)
            
            if st.button("💾 保存更改", type="primary", use_container_width=True):
                st.session_state.user_profile.update({
                    "name": new_name, "gender": new_gender, "enrollment_year": new_year,
                    "mbti": new_mbti, "campus": new_campus, "time_commit": new_time,
                    "college": new_college, "major": new_major, "bio": new_bio
                })
                st.session_state.edit_mode = False
                st.rerun()

        elif is_empty:
            # --- 💡 新增引导模式：如果姓名还是 "--"，就显示引导按钮，不显示横杠 ---
            st.info("👋 你的档案目前还是初始状态。完善后 AI 匹配将更加精准！")
            if st.button("✨ 立即完善个人档案", type="primary", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()

        else:
            # --- 📖 阅览模式 (完全保留你的原版代码) ---
            col_t, col_b = st.columns([4, 1])
            with col_t:
                st.markdown(f"### {profile['name']}  `{profile['gender']}`")
            with col_b:
                if st.button("✏️ 编辑", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()
            st.markdown(f"🎓 **{profile['college']}** · {profile['major']} ({profile['enrollment_year']}级)")
            st.markdown(f"🏷️ `{profile['mbti']}` · `{profile['campus']}` · `{profile['time_commit']}`")
            st.info(profile['bio'])

    # ==========================================
    # 模块 2：投递记录 (完全保留你的原版代码)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📬 投递进度")
    applied_clubs = st.session_state.get('applied_clubs', [])
    
    if not applied_clubs:
        st.info("🎒 目前还没有投递记录。")
    else:
        # 去重显示
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