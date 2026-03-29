import streamlit as st
from core.state_manager import navigate_to
from core.recsys_engine import get_dynamic_tag_pairs, get_top_recommended_club

def render():
    profile = st.session_state.get('user_profile', {})
    
    # ==========================================
    # 🚨 门禁系统：检查是否为未填写的空档案
    # ==========================================
    # 如果 profile 为空，或者 name 字段没有填写（初始状态）
    if not profile or not profile.get('name'):
        st.warning("📋 为了提供精准的 AI 匹配，请先完成基础破冰信息填写。")
        if st.button("前往破冰引导页", type="primary", use_container_width=True):
            # 引导新用户进入专用的破冰引导流
            navigate_to('onboarding')
        return # 拦截后续渲染

    st.title("🎴 发现你的热爱")
    
    # ==========================================
    # 顶部全局导航栏
    # ==========================================
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 发现主页", use_container_width=True):
            navigate_to('home_dashboard')
    with col_nav2:
        st.button("🎴 沉浸式 AI 匹配", use_container_width=True, disabled=True)
    with col_nav3:
        if st.button("👤 我的与投递", use_container_width=True):
            navigate_to('profile')
    st.markdown("---")

    # 初始化状态机
    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []
        
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
        
    # 1. 结合历史记忆，动态获取拔河卡片 (决策树引擎)
    if 'dynamic_pairs' not in st.session_state:
        with st.spinner("🧠 算法正在根据你的潜意识，实时生成深度测试分支..."):
            st.session_state.dynamic_pairs = get_dynamic_tag_pairs(
                user_profile=st.session_state.get('user_profile', {}),
                swipe_history=st.session_state.swipe_history,
                num_pairs=4
            )
        
    current_idx = st.session_state.swipe_index
    total_cards = len(st.session_state.dynamic_pairs)
    
    # 2. 核心：纯 Python 高保真 UI 渲染区域
    if current_idx < total_cards:
        st.markdown(f"**匹配进度：{current_idx + 1} / {total_cards}**")
        pair = st.session_state.dynamic_pairs[current_idx]
        
        # 静态双卡片对峙 UI (纯 CSS 渲染，安全且美观)
        col1, col2, col3 = st.columns([4, 1, 4])
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FF5757, #FF8235); padding: 50px 10px; border-radius: 16px; color: white; text-align: center; font-size: 22px; font-weight: bold; box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
                {pair['left']}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 55px; font-size: 20px; color: #aaa; font-weight: 800;'>VS</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1A73E8, #34A853); padding: 50px 10px; border-radius: 16px; color: white; text-align: center; font-size: 22px; font-weight: bold; box-shadow: 0 8px 16px rgba(0,0,0,0.15);">
                {pair['right']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 恢复原生拔河滑块
        choice = st.select_slider(
            label="你的直觉偏向是？",
            options=[
                f"👈 绝对偏向：{pair['left']}", 
                f"偏向：{pair['left']}", 
                "⚖️ 中立", 
                f"偏向：{pair['right']}", 
                f"绝对偏向：{pair['right']} 👉"
            ],
            value="⚖️ 中立",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 数据提交按钮
        if st.button("锁定选择进入下一题 ➡️", type="primary", use_container_width=True):
            st.session_state.swipe_history.append({
                "left": pair['left'],
                "right": pair['right'],
                "choice": choice
            })
            st.session_state.swipe_index += 1
            st.rerun()
            
    else:
        # ==========================================
        # 3. 算法计算与转化拦截页面
        # ==========================================
        with st.spinner('🎯 正在锁定最佳匹配项...'):
            best_club_id = get_top_recommended_club(
                st.session_state.get('user_profile', {}), 
                st.session_state.swipe_history
            )
            
        st.session_state.current_club_view = best_club_id
        st.session_state.from_ai_recommendation = True
        
        st.success("✨ 基于你的直觉，AI 大脑已锁定最佳契合度社团！")
        st.info("侧边栏 AI 助手已就绪，正在为你生成个性化匹配分析 👇")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👀 立即查看专属推荐", type="primary", use_container_width=True):
                # 清空本轮状态，为下一次深度决策树铺垫
                if 'dynamic_pairs' in st.session_state:
                    del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                navigate_to('club_detail')
        with col2:
            if st.button("❌ 感觉不对，重新测试", use_container_width=True):
                # 触发纯随机探索机制
                if 'dynamic_pairs' in st.session_state:
                    del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                st.session_state.swipe_history = [] 
                st.rerun()