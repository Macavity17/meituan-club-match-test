import streamlit as st
import streamlit.components.v1 as components
import json
import base64
from core.state_manager import navigate_to
from core.recsys_engine import get_dynamic_tag_pairs, get_top_recommended_club

def b64_encode(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def render():
    st.title("🎴 发现你的热爱")
    
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

    if 'swipe_history' not in st.session_state:
        st.session_state.swipe_history = []
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
        
    if 'dynamic_pairs' not in st.session_state:
        with st.spinner("🧠 算法正在根据你的潜意识，实时生成深度测试分支..."):
            st.session_state.dynamic_pairs = get_dynamic_tag_pairs(
                user_profile=st.session_state.get('user_profile', {}),
                swipe_history=st.session_state.swipe_history,
                num_pairs=4
            )
        
    current_idx = st.session_state.swipe_index
    total_cards = len(st.session_state.dynamic_pairs)
    
    if current_idx < total_cards:
        st.markdown(f"**匹配进度：{current_idx + 1} / {total_cards}**")
        pair = st.session_state.dynamic_pairs[current_idx]
        
        uid = f"{current_idx}"

        custom_html = f"""
        <style>
            #swipe-container-{uid} {{ width: 100%; max-width: 400px; margin: 0 auto; text-align: center; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; position: relative; padding-bottom: 20px; }}
            #card-viewport-{uid} {{ position: relative; height: 230px; margin-bottom: 20px; display: flex; justify-content: center; align-items: center; perspective: 1000px; }}
            
            .card {{ position: absolute; width: 140px; height: 190px; border-radius: 18px; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 20px; font-weight: bold; box-shadow: 0 10px 25px rgba(0,0,0,0.25); transition: transform 0.15s ease-out, opacity 0.1s ease-out, z-index 0.0s linear; overflow: hidden; }}
            .card .card-type {{ font-size: 10px; opacity: 0.7; margin-bottom: 8px; font-weight: normal; text-transform: uppercase; letter-spacing: 1px;}}
            
            #card-left-{uid} {{ background: linear-gradient(135deg, #FF5757, #FF8235); transform: translateX(-65px) rotate(-10deg) scale(0.95); opacity: 0.9; z-index: 1; }}
            #card-right-{uid} {{ background: linear-gradient(135deg, #1A73E8, #34A853); transform: translateX(65px) rotate(10deg) scale(0.95); opacity: 0.9; z-index: 1; }}
            
            #slider-{uid} {{ width: 95%; margin: 25px 0 10px 0; cursor: pointer; accent-color: #FF4B4B;}}
            .slider-labels {{ display: flex; justify-content: space-between; padding: 0 15px; color: #777; font-size: 12px; margin-bottom: 25px; }}
            .slider-labels span.dot {{ color: #ccc; font-weight: normal; }}
            
            #confirm-btn-{uid} {{ width: 100%; padding: 12px; background: #FF4B4B; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; transition: background 0.1s; opacity: 0.8; box-sizing: border-box; margin-top: 10px; }}
            #confirm-btn-{uid}:not(.disabled):hover {{ background: #E03D3D; opacity: 1; }}
            #confirm-btn-{uid}.disabled {{ background: #ccc; cursor: not-allowed; }}
        </style>

        <div id="swipe-container-{uid}">
            <div id="card-viewport-{uid}">
                <div id="card-left-{uid}" class="card">
                    <span class="card-type">气质类型 A</span>
                    {pair['left']}
                </div>
                <div id="card-right-{uid}" class="card">
                    <span class="card-type">气质类型 B</span>
                    {pair['right']}
                </div>
            </div>

            <input type="range" id="slider-{uid}" min="1" max="5" value="3">
            <div class="slider-labels">
                <span>绝对A</span>
                <span class="dot">·</span>
                <span>中立</span>
                <span class="dot">·</span>
                <span>绝对B</span>
            </div>
            
            <a id="confirm-btn-{uid}" class="disabled" href="javascript:void(0);">锁定当前选择 (需移动滑块)</a>
        </div>

        <script>
            (function() {{
                const sl = document.getElementById('slider-{uid}');
                const cL = document.getElementById('card-left-{uid}');
                const cR = document.getElementById('card-right-{uid}');
                const btn = document.getElementById('confirm-btn-{uid}');
                
                // 【修复Bug 3】: 动态获取父级真实 URL，兼容本地与 Cloud
                const parentUrl = document.referrer ? document.referrer.split('?')[0] : window.location.origin;

                const labelsL = "👈 绝对偏向：{pair['left']}";
                
                // 【修复Bug 1】: 修改了拼写错误的变量名 labelsRR -> labelsR
                const labelsR = "绝对偏向：{pair['right']} 👉";

                const labelsL1 = "偏向：{pair['left']}";
                const labelsR1 = "偏向：{pair['right']}";
                
                // 【修复Bug 4】: 统一文案为“中立”
                const labelM = "⚖️ 中立"; 

                const get_choice_text = (val) => {{
                    if (val === 1) return labelsL;
                    if (val === 2) return labelsL1;
                    if (val === 3) return labelM;
                    if (val === 4) return labelsR1;
                    if (val === 5) return labelsR; 
                }}

                sl.addEventListener('input', (e) => {{
                    const val = parseInt(e.target.value);
                    
                    if (val !== 3) {{
                        btn.className = "";
                        btn.innerText = "锁定选择 ➡️ " + get_choice_text(val).replace('⚖️ ', '');
                    }} else {{
                        btn.className = ""; // 允许中立时点击跳过
                        btn.innerText = "跳过此题 ➡️";
                    }}

                    if (val === 3) {{
                        cL.style.transform = "translateX(-65px) rotate(-10deg) scale(0.95)";
                        cL.style.opacity = "0.9";
                        cL.style.zIndex = "1";
                        cR.style.transform = "translateX(65px) rotate(10deg) scale(0.95)";
                        cR.style.opacity = "0.9";
                        cR.style.zIndex = "1";
                    }} else if (val < 3) {{
                        let scale = 1 + (3 - val) * 0.1;
                        let move = -65 + (3 - val) * 45; 
                        cL.style.transform = `translateX(${{move}}px) rotate(0deg) scale(${{scale}})`;
                        cL.style.opacity = "1";
                        cL.style.zIndex = "10";
                        
                        let sR = 0.9 - (3 - val) * 0.15;
                        let mR = 65 + (3 - val) * 10;
                        cR.style.transform = `translateX(${{mR}}px) rotate(20deg) scale(${{sR}})`;
                        cR.style.opacity = 0.9 - (3 - val) * 0.4;
                        cR.style.zIndex = "1";
                    }} else {{
                        let scale = 1 + (val - 3) * 0.1;
                        let move = 65 - (val - 3) * 45; 
                        cR.style.transform = `translateX(${{move}}px) rotate(0deg) scale(${{scale}})`;
                        cR.style.opacity = "1";
                        cR.style.zIndex = "10";
                        
                        let sL = 0.9 - (val - 3) * 0.15;
                        let mL = -65 - (val - 3) * 10;
                        cL.style.transform = `translateX(${{mL}}px) rotate(-20deg) scale(${{sL}})`;
                        cL.style.opacity = 0.9 - (val - 3) * 0.4;
                        cL.style.zIndex = "1";
                    }}
                    
                    const choice_data = JSON.stringify({{
                        "left": "{pair['left']}",
                        "right": "{pair['right']}",
                        "idx": "{current_idx}",
                        "choice": get_choice_text(val)
                    }});
                    
                    btn.href = parentUrl + "?swipe_payload=" + btoa(unescape(encodeURIComponent(choice_data)));
                    btn.target = "_parent"; 
                }});
            }})();
        </script>
        """
        
        # 【修复Bug 2】: 扩大了 iframe 高度，从 380 提升到 430，防止按钮被切断
        components.html(custom_html, height=430)

    else:
        with st.spinner('🎯 正在锁定最佳匹配项...'):
            best_club_id = get_top_recommended_club(
                st.session_state.get('user_profile', {}), 
                st.session_state.swipe_history
            )
            
        st.session_state.current_club_view = best_club_id
        st.session_state.from_ai_recommendation = True
        
        st.success("✨ 基于你的直觉，AI 大脑已锁定最佳契合度社团！")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👀 立即查看专属推荐理由", type="primary", use_container_width=True):
                if 'dynamic_pairs' in st.session_state:
                    del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                navigate_to('club_detail')
        with col2:
            if st.button("❌ 感觉不对，重新测试", use_container_width=True):
                if 'dynamic_pairs' in st.session_state:
                    del st.session_state.dynamic_pairs
                st.session_state.swipe_index = 0
                st.session_state.swipe_history = [] 
                st.rerun()