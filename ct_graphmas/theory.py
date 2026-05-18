"""Theory cards that connect the three project papers to the product design."""

from __future__ import annotations


THEORY_MODELS = [
    {
        "id": "adapt",
        "title": "ADAPT 伴学模式",
        "paper": "超越工具范式：类主体性多智能体协作算法思维培养的 ADAPT 伴学模式设计与研究",
        "tagline": "在 CT-GraphMAS 中，ADAPT 不是另起一套流程，而是教学模式下的个性化伴学调度策略。",
        "stages": [
            {"key": "A", "name": "Assess", "label": "诊断卡点", "detail": "识别学生当前卡在概念、流程、调试还是情绪信心。"},
            {"key": "D", "name": "Design", "label": "设计支架", "detail": "根据最近发展区选择问题分解、示例、反例或测试样例。"},
            {"key": "A", "name": "Act", "label": "行动尝试", "detail": "让学生完成一个小步骤，而不是一次接收完整程序。"},
            {"key": "P", "name": "Practice", "label": "练习验证", "detail": "通过正常样例、边界样例和错误样例验证理解。"},
            {"key": "T", "name": "Transfer", "label": "迁移复盘", "detail": "把本次经验迁移到新的变量、循环、函数或项目任务。"},
        ],
        "system_hooks": [
            "L1 把学生输入诊断为概念、流程、调试或情绪信心卡点",
            "L2 依据画像选择 P1/P2/P4 作为支架组合",
            "知识图谱提供学生掌握度、先修关系、典型错误和相关知识",
            "L3 把支架转成一个可执行的小行动和迁移复盘问题",
        ],
    },
    {
        "id": "coder",
        "title": "C-O-D-E-R 课堂范式",
        "paper": "从“工具”到“类主体”：多智能体协同下中学信息科技课堂的 C-O-D-E-R 范式研究",
        "tagline": "在 CT-GraphMAS 中，C-O-D-E-R 是教师组织项目式编程课堂时的任务编排方式。",
        "stages": [
            {"key": "C", "name": "Contextual Activation", "label": "情境激活", "detail": "用真实校园任务唤起需求、用户和约束。"},
            {"key": "O", "name": "Organized Orchestration", "label": "组织编排", "detail": "教师、学生和智能体共同确定路径、分组与支架强度。"},
            {"key": "D", "name": "Development Collaboration", "label": "协同开发", "detail": "配对编程智能体提供局部提示，学生完成自己的程序表达。"},
            {"key": "E", "name": "Error Debugging", "label": "循环调试", "detail": "代码检查智能体基于报错、样例和变量跟踪进行调试。"},
            {"key": "R", "name": "Reflective Reconstruction", "label": "反思重构", "detail": "思维复盘智能体沉淀问题分解、抽象建模、算法设计和调试评价。"},
        ],
        "system_hooks": [
            "C 阶段由需求分析智能体与 P1 承接，帮助学生澄清情境、用户和输入输出",
            "O 阶段由 L1 按学生画像、任务类型和图谱相关知识编排路径",
            "D 阶段由 P2/P3 承接，把需求转成变量、数据结构和伪代码",
            "E 阶段由 P4 与代码检查智能体承接，依据报错、样例和边界定位",
            "R 阶段由 L3 与思维复盘智能体承接，形成可迁移的计算思维表达",
        ],
    },
    {
        "id": "ct_graphmas",
        "title": "CT-GraphMAS 架构",
        "paper": "CT-GraphMAS: A Knowledge Graph-Enhanced Multi-Agent System for Computational Thinking-Oriented Programming Tutoring",
        "tagline": "CT-GraphMAS 是底层系统架构，负责把日常答疑、教学流程、图谱相关知识和门控评价统一起来。",
        "stages": [
            {"key": "L1", "name": "Cognitive Integrator", "label": "感知与认知整合", "detail": "诊断任务类型、学生画像、知识节点和风险边界。"},
            {"key": "L2", "name": "CT Reasoning Agents", "label": "计算思维推理", "detail": "P1/P2/P3/P4 围绕分解、建模、算法和调试协同。"},
            {"key": "L3", "name": "Interaction Presenter", "label": "交互呈现", "detail": "以同伴、导师或教练风格输出，并执行反代写门控。"},
            {"key": "KG", "name": "Route Evidence", "label": "图谱与相关知识", "detail": "依据当前路由节点选择必要图谱关系和少量高相关知识，避免过量知识注入。"},
        ],
        "system_hooks": [
            "日常通用模式：少量图谱相关知识 + 必要提示，适合学生快速自助",
            "教学模式：ADAPT/C-O-D-E-R 流程 + 智能体调度，适合课堂任务推进",
            "动态图谱路由控制相关知识边界，少量高相关知识控制语料注入量",
            "反代写门控保证反馈克制、可解释、可监督",
        ],
    },
]


DESIGN_PRINCIPLES = [
    {
        "title": "超越代码生成器",
        "body": "系统不以最快生成完整代码为目标，而以帮助学生经历可解释、可验证、可迁移的计算思维过程为目标。",
    },
    {
        "title": "类主体协同",
        "body": "智能体被设计成教师可编排的课堂角色，包括需求分析、逻辑架构、配对编程、代码检查与思维复盘。",
    },
    {
        "title": "相关知识可追溯",
        "body": "每次反馈都暴露图谱策略、相关知识节点和门控结果，方便教师监督与校准。",
    },
    {
        "title": "克制式支架",
        "body": "系统默认提供问题拆解、伪代码、局部检查和样例验证，避免直接代写造成去技能化风险。",
    },
]


def theory_payload() -> dict[str, object]:
    return {"models": THEORY_MODELS, "principles": DESIGN_PRINCIPLES}
