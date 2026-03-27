import time

# ==========================================
# 【生产环境预留】真实的 OpenAI API 调用逻辑
# 结合用户的静态画像和动态高分滑动特征，通过 Prompt 工程生成真正的千人千面解析。
# 当前 Demo 环境为了保证秒开和零成本，暂时注释，使用下方的 Mock 逻辑替代。
# ==========================================
# import openai
# import os
#
# def generate_real_llm_reasoning(user_profile, swipe_history, club_info):
#     """调用真实的 LLM 接口生成推荐理由"""
#     openai.api_key = os.getenv("OPENAI_API_KEY")  # 从 Streamlit Secrets 读取
#
#     # 1. 提取高分关键词 (极性偏好)
#     preferred_tags = [
#         item['left'] if item['left'] in item['choice'] else item['right']
#         for item in swipe_history if "偏向" in item['choice']
#     ]
#
#     # 2. 构造 System Prompt (设定 AI 产品经理要求的角色与语气)
#     system_prompt = (
#         "你现在是高校社团招新平台的专属 AI 匹配分析师。你的语气要热情、专业、懂年轻人。"
#         "你需要向新生解释为什么推荐这个社团，让他产生‘你真懂我’的 Aha Moment。"
#         "请不要复述用户的输入，而是像一个有洞察力的学长/学姐一样直接给出结论。"
#     )
#
#     # 3. 构造 User Prompt (注入多模态上下文数据)
#     user_prompt = f"""
#     【新生基础画像】
#     MBTI: {user_profile.get('mbti')}
#     每周可用时间: {user_profile.get('time_commit')}
#     【行为偏好标签（最高分）】: {', '.join(preferred_tags)}
#
#     【匹配到的目标社团信息】
#     名称: {club_info.get('name')}
#     口号: {club_info.get('slogan')}
#     核心标签: {', '.join(club_info.get('tags', []))}
#     组织架构: {club_info.get('architecture', [])}
#
#     【任务】请结合以上特征，写一段 150 字以内的专属推荐语，重点解释该新生的特质如何与社团完美契合，并给出具体的社团部门投递建议。
#     """
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo", # 生产可替换为 gpt-4o 或 kimi 等
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             temperature=0.7
#         )
#         return response.choices[0].message['content']
#     except Exception as e:
#         return f"AI 助手开小差了：{str(e)}"

# ==========================================
# 【Demo 环境】高拟真 Mock 逻辑
# ==========================================
def generate_match_reasoning(user_profile, swipe_history, club_info):
    """
    模拟大语言模型 (LLM) 的动态生成逻辑。
    """
    mbti = user_profile.get('mbti', '未知')
    time_commit = user_profile.get('time_commit', '未知')
    
    preferred_tags = []
    for item in swipe_history:
        if "偏向" in item['choice']:
            tag = item['left'] if item['left'] in item['choice'] else item['right']
            preferred_tags.append(tag)
            
    club_name = club_info.get('name', '该社团')
    club_tags = club_info.get('tags', [])
    departments = club_info.get('architecture', [])
    
    matched_tags = list(set(preferred_tags) & set(club_tags))
    
    greeting = f"嗨，基于你是 **{mbti}** 人格，以及预期每周投入 **{time_commit}**，我为你进行了深度多维解析：\n\n"
    
    if matched_tags:
        reasoning = f"💡 **基因共振**：我注意到你在刚才的直觉测试中，对「**{' / '.join(matched_tags)}**」表现出了明确的偏好。这与【{club_name}】的底层基调发生了强烈的共振。\n\n"
    else:
        reasoning = f"💡 **隐式特征互补**：虽然表面上的标签对决你没有直接命中它，但我们的统计算法发现，拥有与你类似底层特征矩阵的同学，最终都在【{club_name}】找到了极高的归属感。\n\n"
        
    if departments:
        rec_dept = departments[0]['department']
        dept_role = departments[0]['role']
        action = f"🎯 **落地建议**：为了最大化你的性格优势，我强烈建议你优先考虑他们的**【{rec_dept}】**。在那里你可以深度参与『*{dept_role}*』，这绝对是为你量身定制的舞台！"
    else:
        action = "🎯 **落地建议**：别犹豫，立刻点击了解更多或者直接投递吧！"

    return greeting + reasoning + action

def stream_mock_response(text):
    """
    Generator：模拟 LLM 打字机输出效果 (Typewriter Effect)
    配合 st.write_stream 使用，极大提升真实感
    """
    for chunk in text.split(" "):
        yield chunk + " "
        time.sleep(0.05)