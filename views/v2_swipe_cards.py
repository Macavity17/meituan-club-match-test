import streamlit as st
from core.state_manager import navigate_to

# 模拟从 keyword_matrix.json 读取的对抗词库 (后续会通过 recsys_engine 动态获取)
MOCK_KEYWORD_PAIRS = [
    {"left": "硬核技术研究", "right": "商业落地探索"},
    {"left": "高强度实战竞技", "right": "基础体能与塑形"},
    {"left": "社会价值与共情", "right": "底层技术与效率"},
    {"left": "沉浸式剧情体验", "right": "硬核机制与对抗"}
]

def render():
    st.title("🎴 发现你的热爱")
    
    # 初始化当前翻卡进度条
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
        
    current_idx = st.session_state.swipe_index
    
    # 核心流转逻辑：每翻 3 张关键词卡，就推 1 个社团卡片
    if current_idx < 3:
        st.markdown(f"**匹配进度：{current_idx + 1} / 3**")
        st.markdown("凭借第一直觉，拖动滑块选择你更倾向的社团特质：")
        
        pair = MOCK_KEYWORD_PAIRS[current_idx]
        
        # 拔河组件 (Tug of War)
        choice = st.select_slider(
            label="你的偏好是？",
            options=[
                f"👈 绝对偏向：{pair['left']}", 
                f"偏向：{pair['left']}", 
                "⚖️ 中立 / 都可以", 
                f"偏向：{pair['right']}", 
                f"绝对偏向：{pair['right']} 👉"
            ],
            value="⚖️ 中立 / 都可以",
            label_visibility="collapsed" # 隐藏默认 label 提升沉浸感
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 提交当前选择并压入历史序列
        if st.button("下一张 ➡️", type="primary", use_container_width=True):
            st.session_state.swipe_history.append({
                "left": pair['left'],
                "right": pair['right'],
                "choice": choice
            })
            st.session_state.swipe_index += 1
            st.rerun()
            
    else:
        # 翻了 3 张卡后，触发社团推荐拦截
        st.success("✨ 基于你的前置选择，我们为你找到了一个高潜匹配社团！")
        
        # TODO: 这里后续由 recsys_engine.py 根据滑动方差和历史计算得出，目前仅做 UI 占位
        st.markdown("### 🏆 AI与数据创新实验室")
        st.markdown("**Slogan:** 用数据驱动决策，以 AI 赋能未来")
        st.info("💡 **AI 匹配理由:** 刚才你选择了“硬核技术研究”，这与该实验室的底层基调高度吻合。")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👀 了解看看", type="primary", use_container_width=True):
                # 将要查看的社团 ID 写入状态，并跳转详情页
                st.session_state.current_club_view = "c_001"
                navigate_to('club_detail')
        with col2:
            if st.button("❌ 不感兴趣，继续刷", use_container_width=True):
                # 重置当前轮次进度，继续下一轮拔河
                st.session_state.swipe_index += 1 
                st.rerun()