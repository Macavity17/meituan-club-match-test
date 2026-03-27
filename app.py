import streamlit as st

# 配置页面基础信息
st.set_page_config(
    page_title="Pipeline Test | Meituan AI PM",
    page_icon="🛠️",
    layout="centered"
)

# 页面主标题
st.title("Meituan AI PM Challenge - Deployment Pipeline Test")

st.markdown("---")
st.write("当前处于 Phase 1：管道连通性测试阶段。旨在验证 GitHub 到 Streamlit Community Cloud 的自动化部署链路。")

# 极简交互组件，验证 Streamlit 的响应能力
if st.button("启动连通性测试", type="primary"):
    st.success("🎉 Pipeline 连通成功！基础设施已就绪，随时可以开展 Phase 2 的核心业务逻辑开发。")
    st.balloons() # 加点视觉反馈，确认前端渲染完全正常