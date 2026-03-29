# 🎴 翻得 (Find) - 社团招新智能匹配平台
> **翻得，find my club！**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://find-my-club-by-paxon.streamlit.app/) 

## 🎯 需求洞察与产品定位 (Project Context)
本项目为响应**「社团招新智能匹配平台」**需求而设计的全栈产品 Demo。
针对高校社团招新中存在的三大核心痛点，我们结合 AI 技术给出了全新的产品解法：
1. **信息不对称** ➡️ 引入 **AI 智能解析**，将干瘪的社团官话转化为基于新生个人特质的“学长式”匹配报告。
2. **难以快速匹配** ➡️ 摒弃传统的“填表与列表搜索”，首创 **「沉浸式拔河 (Tug of War)」** 潜意识抽卡交互，动态捕捉隐式偏好。
3. **报名流程繁琐** ➡️ 实现 **「一键投递 + 进度追踪」** 闭环，集成在个人主页，告别加群扫码填问卷的繁琐体验。

在设计原则上，本项目**优先呈现产品结构和功能设计**，并为未来的商业化技术落地预留了完整的架构蓝图。

---

## ✨ 核心产品结构与功能设计 (Product Structure & Features)

本平台由 5 大核心模块构建了完整的“发现-匹配-决策-投递”用户体验流：

### 1. 破冰与画像采集 (Onboarding)
*   **极简采集**：拒绝长篇大论的问卷，仅需提供 `MBTI`、`常驻校区`、`每周可用时间` 3 个核心基准标签。
*   **严密门禁**：底层状态机实现强制拦截，未完善基础画像的用户无法进入推荐流，保证推荐算法输入数据的纯净度。

### 2. 潜意识拔河抽卡 (Tug-of-War UI)
*   **交互创新**：将社团的复杂特征提取为“核心对立基因”（如：硬核技术研究 VS 商业落地探索）。
*   **隐式挖掘**：用户通过拖动滑块（绝对偏向/中立/偏向）凭直觉做出选择，极大地降低了新生的认知负荷与决策压力。

### 3. AI 专属详情与防流失闭环 (AI Insights & Smart Loop)
*   **个性化解读**：AI 助手根据用户的 MBTI 和历史翻卡记录，动态生成个性化的“匹配亮点”，打破信息壁垒。
*   **反馈拦截系统**：用户离开详情页前需进行 `1-5星` 打分。低分直接回滚至抽卡流（继续探索）；高分（≥4分）且完成投递后，弹出“逃生舱”导流至广场，避免用户陷入信息疲劳。

### 4. 社团发现广场 (Dashboard)
*   **双轨内容流**：为明确目标的用户提供直观的“热门社团”网格，同时提供全站“近期动态”瀑布流，辅助用户从日常活动的侧面了解社团氛围。

---

## 🧠 核心推荐算法逻辑 (RecSys Logic)
本 Demo 不使用僵化的 `if-else` 标签匹配，而是设计了一套基于**先验概率与隐式特征挖掘**的泛化推荐引擎：

1. **粗排过滤 (Hard Filtering)**：利用用户的物理属性（校区）与时间承诺（Time Commit），进行第一层漏斗过滤，剔除绝对不匹配项。
2. **特征向量化 (Vectorization)**：用户的 MBTI 和滑动选择均被视为特征向量。例如，滑块的“绝对偏向”带来高信息增益权重，而“中立”带来低权重。
3. **概率矩阵映射 (Probability Matrix)**：引入 `global_statistics.json` 作为推荐大脑。将用户的特征向量投射到全局历史统计矩阵中，计算各个社团的后验匹配概率（Base Score + Dynamic Score），最终输出 Top 1 结果。

---

## 🏗️ 生产环境预留蓝图 (Production-Ready Blueprints)
遵循“优先呈现产品设计，不纠结于技术细节”的原则，我们在 Demo 中使用了静态 JSON 和本地 Mock 逻辑。但**我们在源码结构中，已为全量生产环境预留了以下技术接入点**：

1. **真实大模型 (LLM) 无缝接入** 
   * *当前状态*：在 `core/mock_llm.py` 中使用高拟真逻辑结合打字机特效模拟。
   * *预留蓝图*：已封装完整的 `generate_real_llm_reasoning` 接口及系统级 Prompt。只需填入 API Key 即可零成本切换至真实的 OpenAI/通义千问等大模型 API 进行流式推理。
2. **数据飞轮与反向传播 (Data Flywheel)**
   * *当前状态*：用户的打分行为记录在单次 Session 状态机中。
   * *预留蓝图*：`update_global_matrix_with_feedback` 接口已留存奖励计算逻辑。在连接真实数据库（如 PostgreSQL/Neo4j）后，高分打分将反向更新概率矩阵中的 `tag_affinities`，实现系统越用越准的数据飞轮效应。
3. **MAB 探索与利用策略 (Exploration vs. Exploitation)**
   * *预留蓝图*：抽卡流预留了多臂老虎机（Multi-Armed Bandit）算法入口。未来可按 80% 比例曝光高收益标签，20% 比例混入长尾标签用于收集数据，打破新生的“信息茧房”。

---

## 📁 工程架构 (Repository Structure)

采用了高内聚、低耦合的 `MVC` 变体架构，将核心算法与视图层严格解耦：

```text
meituan-club-match/
├── app.py                       # 主程序入口与全局路由分发中心
├── requirements.txt             # 依赖清单
├── README.md                    # 项目说明文档
├── data/                        # 数据底座
│   ├── mock_clubs.json          # 实体数据库 (基础信息/Tags/架构/新闻)
│   └── global_statistics.json   # 推荐大脑：全局统计先验矩阵 (历史沉淀概率分布)
├── core/                        # 核心逻辑层 (Engine)
│   ├── __init__.py
│   ├── state_manager.py         # 状态机管理与全局无缝路由
│   ├── recsys_engine.py         # 推荐引擎 (融合基础画像、行为方差与历史概率矩阵)
│   └── mock_llm.py              # AI 大脑 (侧边栏动态文案生成 / LLM 接入网关)
├── views/                       # 表现层 (UI Components)
│   ├── __init__.py
│   ├── v1_onboarding.py         # 极简破冰页 (收集关键基准画像)
│   ├── v2_swipe_cards.py        # 沉浸式 AI 抽卡匹配页 (Tug of War 核心交互)
│   ├── v3_club_detail.py        # 详情转化页 (AI 专属解读 + 强制打分拦截)
│   ├── v4_home_dashboard.py     # 发现广场 (双轨内容流：热门推荐 & 新鲜事)
│   ├── v5_profile.py            # 个人中心 (画像展示 + 投递进度追踪)
|   └── v6_about.py
└── assets/
    └── styles.css               # 自定义样式表 (待拓展)
---

## 🛠️ 技术栈与快速启动

*   **框架**: `Python 3.10+` + `Streamlit`
*   **部署**: Streamlit Community Cloud (原生支持 CI/CD 与 GitHub 联调)

**本地运行测试：**
```bash
# 1. 克隆仓库
git clone [https://github.com/Macavity17/meituan-club-match.git](https://github.com/Macavity17/meituan-club-match.git)
cd meituan-club-match

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
streamlit run app.py
```

---
*Designed & Engineered for Meituan AI PM Challenge.*
