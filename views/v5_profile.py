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
    # 顶部全局导航栏 (扩充为 4 栏)
    # ==========================================
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    with col_nav1:
        if st.button("🏠 发现主页", use_container_width=True):
            navigate_to('home_dashboard')
    with col_nav2:
        if st.button("🎴 沉浸式 AI 匹配", use_container_width=True):
            navigate_to('swipe_cards')
    with col_nav3:
        st.button("👤 我的与投递", use_container_width=True, disabled=True)
    with col_nav4:
        if st.button("ℹ️ 关于", use_container_width=True):
            navigate_to('about')

    st.markdown("---")

    clubs_dict = load_clubs_data()

    # ==========================================
    # 模块 1：个人基础画像 (大 Profile 交互式面板)
    # ==========================================
    st.subheader("📝 我的画像")
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    profile = st.session_state.user_profile
    
    # 为空字段注入默认值，让页面拥有充实感与代入感
    defaults = {
        "name": "Paxon",
        "gender": "男",
        "enrollment_year": "2024",
        "mbti": profile.get("mbti", "ENTP"),
        "campus": profile.get("campus", "卫津路校区"),
        "time_commit": profile.get("time_commit", "3-5小时 (积极参与)"),
        "college": "天津大学",
        "major": "管理科学与工程",
        "bio": "来自青岛，对资产配置和AI大模型有浓厚兴趣。平时喜欢举重、攀岩和射箭。目前正在准备关于员工对AI幻觉容忍度的毕业论文，并积极寻找暑期实习机会。"
    }
    
    for k, v in defaults.items():
        if k not in profile or not profile[k]:
            profile[k] = v

    # 初始化编辑状态机
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    with st.container(border=True):
        if st.session_state.edit_mode:
            # --- ✏️ 编辑模式 UI ---
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("姓名", value=profile["name"])
                
                year_options = ["2022", "2023", "2024", "2025", "2026"]
                year_idx = year_options.index(profile["enrollment_year"]) if profile["enrollment_year"] in year_options else 2
                new_year = st.selectbox("入学年份", year_options, index=year_idx)
                
            with c2:
                gender_options = ["男", "女", "其他", "保密"]
                gender_idx = gender_options.index(profile["gender"]) if profile["gender"] in gender_options else 0
                new_gender = st.selectbox("性别", gender_options, index=gender_idx)
                
            st.markdown("---")
            st.caption("破冰特征标签 (影响 AI 匹配策略)")
            
            # 将破冰的三项紧跟在基本信息之后
            c3, c4, c5 = st.columns(3)
            with c3:
                mbti_opts = ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "其他/暂时保密"]
                mbti_idx = mbti_opts.index(profile["mbti"]) if profile["mbti"] in mbti_opts else 1
                new_mbti = st.selectbox("MBTI 人格", mbti_opts, index=mbti_idx)
            with c4:
                campus_opts = ["北洋园校区", "卫津路校区", "其他"]
                campus_idx = campus_opts.index(profile["campus"]) if profile["campus"] in campus_opts else 1
                new_campus = st.selectbox("主要活动校区", campus_opts, index=campus_idx)
            with c5:
                time_opts = ["1-2小时 (边缘OB)", "3-5小时 (积极参与)", "6小时以上 (核心骨干)"]
                time_idx = time_opts.index(profile["time_commit"]) if profile["time_commit"] in time_opts else 1
                new_time = st.selectbox("预期投入时间", time_opts, index=time_idx)

            st.markdown("---")
            
            c6, c7 = st.columns(2)
            with c6:
                new_college = st.text_input("学校/学院", value=profile["college"])
            with c7:
                new_major = st.text_input("专业", value=profile["major"])

            new_bio = st.text_area("个人简介", value=profile["bio"], height=100)
            
            if st.button("💾 保存档案", type="primary", use_container_width=True):
                # 将输入数据存入状态机实现跨页面持久化
                st.session_state.user_profile.update({
                    "name": new_name,
                    "gender": new_gender,
                    "enrollment_year": new_year,
                    "mbti": new_mbti,
                    "campus": new_campus,
                    "time_commit": new_time,
                    "college": new_college,
                    "major": new_major,
                    "bio": new_bio
                })
                st.session_state.edit_mode = False
                st.rerun()

        else:
            # --- 📖 阅览模式 UI ---
            col_title, col_btn = st.columns([4, 1])
            with col_title:
                st.markdown(f"### {profile['name']}  `{profile['gender']}`")
            with col_btn:
                if st.button("✏️ 编辑", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()
                    
            st.markdown(f"🎓 **教育背景**：{profile['college']} · {profile['major']} ({profile['enrollment_year']}级)")
            st.markdown(f"🏷️ **破冰特征**：`{profile['mbti']}` · `{profile['campus']}` · `{profile['time_commit']}`")
            st.markdown("**📖 个人简介**：")
            st.info(profile['bio'])

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 模块 2：投递与进度跟踪 (保持原样逻辑)
    # ==========================================
    st.subheader("📬 投递进度")
    applied_clubs = st.session_state.get('applied_clubs', [])
    
    if not applied_clubs:
        st.info("🎒 你目前还没有投递任何社团。快去广场或 AI 匹配找找心仪的组织吧！")
    else:
        for club_id in set(applied_clubs): 
            club = clubs_dict.get(club_id)
            if club:
                with st.container(border=True):
                    col_info, col_status = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{club['name']}**")
                        st.caption("已投递简历 | 正在等待社团负责人筛选")
                    with col_status:
                        st.button("查看详情", key=f"view_{club_id}", on_click=lambda c=club_id: (
                            st.session_state.update(
                                current_club_view=c,
                                from_ai_recommendation=False
                                ), 
                            navigate_to('club_detail')
                        ))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # 模块 3：算法反馈足迹
    # ==========================================
    st.subheader("我的打分足迹")
    feedbacks = st.session_state.get('match_feedbacks', [])
    if not feedbacks:
        st.write("暂无打分记录。")
    else:
        for fb in reversed(feedbacks[-5:]):
            club_name = clubs_dict.get(fb['club_id'], {}).get('name', '未知社团')
            st.write(f"- 你为 **{club_name}** 的 AI 匹配推荐打了 **{fb['score']} 星**")