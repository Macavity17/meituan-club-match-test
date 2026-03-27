# 🎴 翻得 (Find) 
> **翻得，find my club！**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://find-my-club-by-paxon.streamlit.app/) 

## 📖 项目背景
本项目为 **美团 AI 产品经理 (AI PM)** 岗位限时考核作品。
针对高校社团招新中存在的“信息不对称”、“填表流程繁琐”、“新生难以准确定位兴趣”等痛点，我们设计了「翻得」—— 一款基于**隐式特征挖掘**与**全局先验概率矩阵**的智能社团匹配平台。

---

## ✨ 核心产品巧思 (The "Aha" Moments)

### 1. 交互革命：从“填表搜索”到“沉浸式拔河 (Tug of War)”
摒弃了传统的“多条件筛选”带来的极高认知负荷。将冗长的社团介绍解构成干练的**基因标签 (Tags)**，并两两配对生成滑块卡片。用户仅需凭直觉进行滑动，系统通过计算选择的**极性与方差**，动态捕捉用户的潜在偏好。

### 2. 万物皆特征，一切皆概率：摒弃 If-Else 的推荐大脑
推荐系统不使用僵化的 `if (MBTI == "INTJ")` 规则，而是基于历史数据沉淀出 `global_statistics.json`（全局统计概率矩阵）。无论是用户的静态画像（每周可用时间），还是动态行为（滑动选项），都被视为特征向量，投射到概率矩阵中计算最终的社团匹配度，真正实现了**泛化推荐**与**隐式特征关联**。

### 3. “上瘾”循环与聪明的逃生舱 (Smart UX Loop)
*   **流量留存：** 用户在详情页看完社团后，必须进行精准度打分才能离开。若未遇到“完美契合(≥4分)”并发生“投递动作”，系统会将用户无缝送回抽卡循环，持续探索。
*   **逃生舱：** 满足上述两大条件时，触发“退出循环”弹窗，将用户导流至内容广场，避免过度疲劳，实现完美的“用完即走，好得还来”的 C 端闭环体验。

---

## 🏗️ 工程文件架构 (Repository Structure)

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
│   └── v5_profile.py            # 个人中心 (画像展示 + 投递进度追踪)
└── assets/
    └── styles.css               # 自定义样式表 (待拓展)
```

---

## 🚀 生产环境预留蓝图 (Production-Ready Blueprints)

考虑到 Streamlit Community Cloud 的内存特性（易休眠、不可直接覆写 GitHub 文件导致 CI/CD 死循环），我们在 Demo 中对部分底层重度操作进行了优雅的降级与 Mock。**但在源码中，我们保留了完整的商业化落地逻辑（已注释），随时可一键解封：**

1. **真实大模型 (LLM) 无缝接入** 
   * *当前状态*：在 `core/mock_llm.py` 中使用高拟真逻辑+打字机特效模拟。
   * *预留蓝图*：已封装完整的 `generate_real_llm_reasoning` 接口。内置了系统级角色提示词（System Prompt），并将用户的高分极性标签作为 Context 注入。只需填入 API Key 即可零成本切换至真实大模型。
2. **数据飞轮与动态闭环更新 (Data Flywheel)**
   * *当前状态*：记录于 Session 状态机中展示。
   * *预留蓝图*：在 `core/recsys_engine.py` 的 `update_global_matrix_with_feedback` 接口中，预留了计算**奖励乘数 (Reward Multiplier)** 及反向传播更新数据库 `tag_affinities` 的逻辑。每一次 C 端打分，都在教平台变得更聪明。
3. **MAB/UCB 探索与利用策略 (Exploration vs. Exploitation)**
   * *当前状态*：标签拔河对决使用随机抽取。
   * *预留蓝图*：架构上预留了统计引擎接口。在真实的流量分发中，将采用多臂老虎机算法，80% 曝光历史高方差/高信息增益的标签（Exploitation），20% 混入长尾标签用于测试数据收集（Exploration）。

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
