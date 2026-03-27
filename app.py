import streamlit as st

# 1. 页面基础配置 (必须在脚本最开头)
st.set_page_config(
    page_title="AI 智能社团匹配 | Meituan PM Challenge",
    page_icon="🎯",
    layout="centered"
)

# 2. 初始化全局状态机 (Session State - 数据阅即焚，但不丢失)
# 只要用户不强制刷新网页，这里面的数据永远存在
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'onboarding' # 默认初始页面
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}           # 存放用户的破冰信息

# 3. 极简路由切换函数
def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun() # 强制前端重新渲染，实现无缝跳转

# ==========================================
# 视图层：V1 - 破冰信息收集页 (Onboarding)
# ==========================================
if st.session_state.current_page == 'onboarding':
    st.title("👋 欢迎来到社团智能匹配平台")
    st.markdown("只需提供 **3个核心信息**，AI 即可为你初始化专属的社团探索卡片！")
    
    # 使用 form 表单，确保用户填完后一次性提交，体验更好
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            mbti = st.selectbox("你的 MBTI 人格是？", 
                              ["INTJ", "ENTP", "INFP", "ENFJ", "ISTJ", "ESTP", "ISFP", "ESFJ", "其他/暂时保密"])
            campus = st.selectbox("主要活动校区", 
                                ["本部核心校区", "软件园校区", "医学院校区"])
        with col2:
            time_commit = st.select_slider("每周愿意投入社团的时间", 
                                         options=["1-2小时 (边缘OB)", "3-5小时 (积极参与)", "6小时以上 (核心骨干)"])
        
        st.markdown("---")
        # 提交按钮
        submitted = st.form_submit_button("生成我的专属匹配卡 🚀", type="primary")
        
        if submitted:
            # 存入 Session State 的持久化字典中
            st.session_state.user_profile = {
                "mbti": mbti,
                "campus": campus,
                "time_commit": time_commit
            }
            # 路由跳转到翻卡页
            navigate_to('swipe_cards')

# ==========================================
# 视图层：V2 - 核心翻卡测试页 (Swipe Cards)
# ==========================================
elif st.session_state.current_page == 'swipe_cards':
    st.title("🎴 核心体验：AI 关键词拔河")
    
    # 这里用于向你（PM）和面试官证明，上一步的数据完美透传过来了！
    st.success("🎉 破冰成功！前端路由已跳转，且你的信息已安全存入内存，未发生丢失：")
    st.json(st.session_state.user_profile)
    
    st.markdown("---")
    st.info("💡 这里将是我们下一步的开发主战场：基于方差和中立权重的 Tug of War（关键词拔河）滑动卡片。")
    
    # 提供返回路径，形成闭环
    if st.button("⬅️ 返回修改破冰信息"):
        navigate_to('onboarding')
