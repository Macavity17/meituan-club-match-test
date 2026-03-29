import streamlit as st
import base64
import json
import urllib.parse

def sync_swipe_payload():
    """
    【核心架构增强】
    雷达拦截器：负责截获前端 iframe (v2_swipe_cards) 通过 URL 传回的数据包，
    将其安全解码并同步到后端的 Python 状态机中。
    """
    params = st.query_params
    
    if 'swipe_payload' in params:
        payload_b64 = params['swipe_payload']
        try:
            # URL 解码 & Base64 解码
            decoded_bytes = base64.b64decode(urllib.parse.unquote(payload_b64))
            payload_json = decoded_bytes.decode('utf-8')
            data = json.loads(payload_json)
            
            idx_from_front = int(data.get('idx', -1))
            
            # 防抖校验与数据落库
            if idx_from_front == st.session_state.get('swipe_index', 0):
                st.session_state.swipe_history.append({
                    "left": data['left'],
                    "right": data['right'],
                    "choice": data['choice']
                })
                st.session_state.swipe_index = st.session_state.get('swipe_index', 0) + 1
            
            # 阅后即焚：清理 URL 参数
            del st.query_params['swipe_payload']
            
        except Exception as e:
            print(f"Payload 同步异常: {e}")
            pass

def init_session_state():
    """初始化全局状态机"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'onboarding' # 默认入口页
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}           # 用户破冰信息
        
    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []          # 用户的滑动打分序列
        
    if 'current_club_view' not in st.session_state:
        st.session_state.current_club_view = None    # 当前正在查看的社团详情
        
    # 新增：翻卡下标状态初始化
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0

    # 🚀 在状态初始化的生命周期中，挂载我们的 URL 雷达拦截器！
    sync_swipe_payload()

def navigate_to(page_name):
    """全局路由跳转触发器"""
    st.session_state.current_page = page_name
    st.rerun()