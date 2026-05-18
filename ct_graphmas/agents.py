"""Three-layer multi-agent dialogue engine for CT-GraphMAS."""

from __future__ import annotations

import re
from typing import Any

from .embedding import concept_hits
from .knowledge_graph import KnowledgeGraphService
from .prompt_workflow import ADAPT_AGENT_DESIGN, CODER_AGENT_DESIGN, prompt_workflow_payload
from .storage import Store


PROFILE_LABELS = {
    "novice": "破冰期新手",
    "intermediate": "建构期中等生",
    "advanced": "自动化期进阶生",
}

STYLE_LABELS = {
    "companion": "同伴型",
    "tutor": "启发导师型",
    "coach": "严格教练型",
}

WORKFLOW_LABELS = {
    "coder": "C-O-D-E-R",
    "adapt": "ADAPT",
    "standard": "标准编程辅导",
}

MODE_LABELS = {
    "daily": "日常通用模式",
    "teaching": "教学模式",
}


class L1CognitiveIntegrator:
    def run(self, message: str, profile: str, workflow: str, mode: str, retrieval: dict[str, Any]) -> dict[str, Any]:
        task_type = self._task_type(message)
        concepts = self._concepts(message, retrieval)
        route = self._route(profile, task_type, concepts, workflow, mode)
        risk_flags = self._risk_flags(message)
        target = retrieval.get("target_micro_concept") or {}
        prompt_meta = prompt_workflow_payload()["prompts"][0]
        return {
            "layer": "L1 感知与认知整合中枢",
            "mode": MODE_LABELS.get(mode, mode),
            "student_profile": PROFILE_LABELS.get(profile, profile),
            "workflow": WORKFLOW_LABELS.get(workflow, workflow),
            "task_type": task_type,
            "student_dilemma": self._dilemma(task_type, message),
            "cognitive_state": self._cognitive_state(retrieval, profile),
            "target_concept": self._target_concept_label(target),
            "kg_context": retrieval.get("kg_state", ""),
            "concepts": concepts,
            "route": route,
            "risk_flags": risk_flags,
            "graph_policy": retrieval["strategy"],
            "prompt_contract": {
                "id": prompt_meta["id"],
                "title": prompt_meta["title"],
                "input": prompt_meta["input"],
                "output": prompt_meta["output"],
            },
            "diagnostic_sentence": self._diagnostic_sentence(task_type, concepts, profile, workflow, mode),
            "orchestration": self._orchestration(workflow, mode),
        }

    @staticmethod
    def _task_type(message: str) -> str:
        lowered = message.lower()
        if any(token in lowered for token in ["traceback", "error", "报错", "错误", "bug", "debug", "调试"]):
            return "语法纠错/调试支持"
        if any(token in message for token in ["设计", "流程", "算法", "步骤", "怎么做", "思路"]):
            return "编程过程与算法组织"
        if any(token in message for token in ["是什么", "为什么", "区别", "概念", "理解"]):
            return "概念问答与迁移理解"
        if "完整代码" in message or "直接写" in message or "代写" in message:
            return "高代写风险请求"
        return "综合编程辅导"

    @staticmethod
    def _concepts(message: str, retrieval: dict[str, Any]) -> list[dict[str, str]]:
        label_lookup = {node["id"]: node["label"] for node in retrieval["subgraph"]["nodes"]}
        seen: set[str] = set()
        concepts: list[dict[str, str]] = []
        target = retrieval.get("target_micro_concept")
        if target:
            node_id = str(target["id"])
            seen.add(node_id)
            concepts.append(
                {
                    "id": str(target.get("concept_id") or node_id),
                    "label": f"{target.get('concept_id')} {target.get('label')}",
                    "source": "kg-intent",
                }
            )
        for node_id, score in concept_hits(message)[:8]:
            if node_id in seen:
                continue
            seen.add(node_id)
            concepts.append({"id": node_id, "label": label_lookup.get(node_id, node_id), "source": f"query:{score}"})
        for node in retrieval["subgraph"]["nodes"]:
            if node["kind"] in {"ct_skill", "python_concept", "error_pattern", "workflow", "strategy", "micro_concept"} and node["id"] not in seen:
                seen.add(node["id"])
                concepts.append({"id": node["id"], "label": node["label"], "source": "graph"})
            if len(concepts) >= 7:
                break
        return concepts

    @staticmethod
    def _dilemma(task_type: str, message: str) -> str:
        clipped = re.sub(r"\s+", " ", message).strip()
        clipped = clipped if len(clipped) <= 120 else clipped[:119] + "…"
        return f"学生当前输入呈现为“{task_type}”，核心表述是：{clipped}"

    @staticmethod
    def _cognitive_state(retrieval: dict[str, Any], profile: str) -> str:
        target = retrieval.get("target_micro_concept")
        profile_label = PROFILE_LABELS.get(profile, profile)
        if not target:
            return f"{profile_label}画像下尚未映射到明确 K 节点，系统采用内置图谱与少量相关知识进行降级支架。"
        mastery = target.get("mastery")
        stage = target.get("stage")
        return (
            f"{profile_label}画像映射到 {target.get('concept_id')} {target.get('label')}，"
            f"认知阶段 Stage {stage}，当前掌握度约为 {mastery}；系统继续查看其 REQUIRES 前置节点以判断支架强度。"
        )

    @staticmethod
    def _target_concept_label(target: dict[str, Any]) -> str:
        if not target:
            return "未映射到明确 K 节点"
        return f"{target.get('concept_id')} {target.get('label')} (Stage {target.get('stage')})"

    @staticmethod
    def _route(profile: str, task_type: str, concepts: list[dict[str, str]], workflow: str, mode: str) -> list[str]:
        concept_ids = {item["id"] for item in concepts}
        route: list[str] = []
        if mode == "daily":
            if "语法纠错" in task_type:
                route.extend(["P4 调试评价", "P1 问题分解"])
            elif "概念问答" in task_type:
                route.extend(["P2 抽象建模", "P1 问题分解"])
            else:
                route.extend(["P1 问题分解", "P3 算法设计"])
        else:
            if workflow == "adapt":
                route.extend(["P1 问题分解", "P2 抽象建模", "P4 调试评价"])
            elif profile == "novice":
                route.extend(["P1 问题分解", "P4 调试评价"])
            elif profile == "advanced":
                route.extend(["P2 抽象建模", "P3 算法设计", "P4 调试评价"])
            else:
                route.extend(["P1 问题分解", "P3 算法设计", "P4 调试评价"])
        if "concept_abstraction" in concept_ids and "P2 抽象建模" not in route:
            route.insert(1, "P2 抽象建模")
        if "语法纠错" in task_type and "P4 调试评价" not in route:
            route.append("P4 调试评价")
        return route[:4]

    @staticmethod
    def _risk_flags(message: str) -> list[str]:
        flags: list[str] = []
        normalized = re.sub(r"\s+", "", message)
        asks_for_full_answer = re.search(r"(给我完整代码|直接写完整|帮我写完|代写|一键生成|直接给答案)", normalized)
        negates_full_answer = re.search(r"(不要|别|不需要|不用)(直接)?(给)?(完整代码|答案|代写)", normalized)
        if asks_for_full_answer and not negates_full_answer:
            flags.append("全盘代写风险")
        if len(message) > 1800:
            flags.append("上下文过长")
        if re.search(r"(考试|测验|作业).*?(答案|完整)", message):
            flags.append("评价场景越界")
        return flags

    @staticmethod
    def _diagnostic_sentence(task_type: str, concepts: list[dict[str, str]], profile: str, workflow: str, mode: str) -> str:
        labels = "、".join(item["label"] for item in concepts[:3]) or "当前任务"
        profile_label = PROFILE_LABELS.get(profile, profile)
        if mode == "daily":
            return f"当前输入更接近“{task_type}”。系统按“{profile_label}”画像提供轻量答疑，知识图谱只注入必要相关知识，优先围绕 {labels} 做定位和下一步提示。"
        return f"当前输入更接近“{task_type}”。系统按“{profile_label}”画像进入 {WORKFLOW_LABELS.get(workflow, workflow)} 教学调度，围绕 {labels} 组织课堂支架和可追溯相关知识。"

    @staticmethod
    def _orchestration(workflow: str, mode: str) -> dict[str, Any]:
        if mode == "daily":
            return {
                "name": "日常通用答疑链",
                "agent_mapping": [
                    {"role": "问题定位", "agent": "P1/P4", "purpose": "快速判断卡点和最小检查路径"},
                    {"role": "概念澄清", "agent": "P2", "purpose": "把变量、数据结构或错误原因讲清楚"},
                ],
                "kg_usage": "检索当前路由子图作为相关知识底座，但只在回答中暴露最相关节点。",
            }
        if workflow == "adapt":
            return {
                "name": "ADAPT 伴学调度链",
                "agent_mapping": [
                    {"role": item["stage"], "agent": item["agents"], "purpose": item["task"], "constraint": item["constraint"]}
                    for item in ADAPT_AGENT_DESIGN
                ],
                "kg_usage": "学生学情、知识点、错误模式和教学语料共同进入路由子图，用于决定支架强度。",
            }
        return {
            "name": "C-O-D-E-R 课堂调度链",
            "agent_mapping": [
                {"role": item["stage"], "agent": item["agents"], "purpose": item["task"], "constraint": item["constraint"]}
                for item in CODER_AGENT_DESIGN
            ],
            "kg_usage": "知识图谱作为课堂相关知识基座，连接任务、知识点、先修关系、错误模式、语料来源与智能体角色。",
        }


class L2Agent:
    name = "L2 Agent"
    node_id = "agent"

    def run(self, message: str, diagnosis: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def _evidence_phrase(self, retrieval: dict[str, Any]) -> str:
        target = retrieval.get("target_micro_concept")
        if target:
            return f"{target.get('concept_id')} {target.get('label')} 及其 2-hop 前置学情"
        nodes = [node["label"] for node in retrieval["subgraph"]["nodes"] if node["kind"] in {"python_concept", "ct_skill", "error_pattern", "micro_concept"}]
        if nodes:
            return "、".join(nodes[:4])
        return "当前问题本身"


class ProblemDecompositionAgent(L2Agent):
    name = "P1 问题分解智能体"
    node_id = "agent_p1"

    def run(self, message: str, diagnosis: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "layer": "L2 计算思维教学推理层",
            "focus": "把问题拆成输入、处理、输出和边界。",
            "thinking": [
                "先找出题目里已经给出的数据或错误信息。",
                "再判断程序要做的最小一步，而不是一次写完整程序。",
                "最后补一个能暴露问题的测试样例。",
            ],
            "output": f"建议先把任务写成四格：输入是什么、要处理哪条规则、输出长什么样、边界在哪里。当前图谱相关知识指向：{self._evidence_phrase(retrieval)}。",
        }


class AbstractionModelingAgent(L2Agent):
    name = "P2 抽象建模智能体"
    node_id = "agent_p2"

    def run(self, message: str, diagnosis: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "layer": "L2 计算思维教学推理层",
            "focus": "把情境转成变量、状态和数据结构。",
            "thinking": [
                "把生活对象压缩为程序变量。",
                "把变化过程标成状态更新。",
                "把重复对象考虑为列表、字典或循环遍历。",
            ],
            "output": f"可以先命名关键变量，再判断它们是单个值、序列还是布尔状态。当前图谱路由关联到 {self._evidence_phrase(retrieval)}，适合作为建模依据。",
        }


class AlgorithmDesignAgent(L2Agent):
    name = "P3 算法设计智能体"
    node_id = "agent_p3"

    def run(self, message: str, diagnosis: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
        task_type = diagnosis.get("task_type", "综合编程辅导")
        return {
            "agent": self.name,
            "layer": "L2 计算思维教学推理层",
            "focus": "形成可执行的伪代码路径。",
            "thinking": [
                "先写自然语言步骤，再对应到 Python 结构。",
                "条件分支只负责选择路径，循环只负责重复动作。",
                "每一步后面都要能说出它验证了什么。",
            ],
            "output": f"针对“{task_type}”，建议用伪代码表达：准备数据 -> 判断/循环 -> 更新结果 -> 输出/测试。先不要扩写成完整代码。",
        }


class DebugEvaluationAgent(L2Agent):
    name = "P4 调试评价智能体"
    node_id = "agent_p4"

    def run(self, message: str, diagnosis: dict[str, Any], retrieval: dict[str, Any]) -> dict[str, Any]:
        likely_error = "运行结果不符合预期"
        lowered = message.lower()
        if "syntaxerror" in lowered or "语法" in message:
            likely_error = "语法结构或缩进/冒号问题"
        elif "nameerror" in lowered or "未定义" in message:
            likely_error = "变量命名或定义顺序问题"
        elif "typeerror" in lowered or "类型" in message:
            likely_error = "类型转换或参数类型问题"
        elif "indexerror" in lowered or "越界" in message:
            likely_error = "索引边界问题"
        return {
            "agent": self.name,
            "layer": "L2 计算思维教学推理层",
            "focus": "用最小测试定位错误并保留学生修复空间。",
            "thinking": [
                f"初步错误线索：{likely_error}。",
                "只改最小可疑位置，避免整段重写。",
                "用一个正常样例和一个边界样例验证。",
            ],
            "output": f"请先标出报错行或异常输出，再用 print/小样例检查变量值。当前相关知识不支持直接替你改完整程序，适合做选择性修复。",
        }


class TeachingGate:
    def evaluate(self, message: str, draft: str, diagnosis: dict[str, Any]) -> dict[str, Any]:
        flags = list(diagnosis.get("risk_flags", []))
        if len(re.findall(r"```|def |class |for |while |if ", draft)) > 8:
            flags.append("可能输出过多完整代码")
        if "全盘代写风险" in flags:
            action = "降级为提示、伪代码和局部检查"
            passed = False
        else:
            action = "通过，保持启发式反馈"
            passed = True
        return {
            "passed": passed,
            "flags": flags,
            "action": action,
            "rubric": {
                "解释准确性": 0.86,
                "修复选择性": 0.9 if passed else 0.78,
                "认知适配性": 0.88,
                "反代写克制": 0.92 if passed else 0.81,
            },
        }


class L3Presenter:
    STYLE_PROMPT_IDS = {
        "companion": "T1",
        "tutor": "T2",
        "coach": "T3",
    }

    def present(
        self,
        message: str,
        profile: str,
        style: str,
        workflow: str,
        mode: str,
        diagnosis: dict[str, Any],
        turns: list[dict[str, Any]],
        retrieval: dict[str, Any],
    ) -> dict[str, Any]:
        style_label = STYLE_LABELS.get(style, "启发导师型")
        prompt_payload = prompt_workflow_payload()
        style_prompt_id = self.STYLE_PROMPT_IDS.get(style, "T2")
        style_prompt = next((item for item in prompt_payload["prompts"] if item["id"] == style_prompt_id), None)
        opening = {
            "companion": "我们先把问题拆小一点。",
            "tutor": "先别急着写完整代码，先抓住最关键的判断点。",
            "coach": "先做诊断，再做最小修复，最后用样例验收。",
        }.get(style, "先别急着写完整代码，先抓住最关键的判断点。")
        workflow_steps = self._workflow_steps(workflow)
        concepts = [item["label"] for item in diagnosis.get("concepts", [])[:4]]
        evidence = retrieval.get("evidence_chunks", [])
        evidence_line = "；".join(f"{item['title']}#{item['chunk_index'] + 1}" for item in evidence[:2]) or "内置知识图谱"
        orchestration = diagnosis.get("orchestration", {})
        mode_line = (
            "日常通用模式下，系统把知识图谱作为低干扰相关知识层，只给学生必要提示和下一步行动。"
            if mode == "daily"
            else f"教学模式下，系统把 {diagnosis.get('workflow')} 流程映射到智能体调度，并让图谱相关知识参与每一步支架选择。"
        )

        paragraphs = [
            opening,
            f"L1 诊断：{diagnosis['diagnostic_sentence']}",
            "L2 协作结论：" + " ".join(turn["output"] for turn in turns),
            f"模式与图谱：{mode_line}相关知识范围控制在当前路由子图、2-hop 学情与少量高相关知识（{evidence_line}）。",
        ]
        if orchestration.get("name"):
            paragraphs.append(f"调度链：{orchestration['name']}。{orchestration.get('kg_usage', '')}")
        if "全盘代写风险" in diagnosis.get("risk_flags", []):
            paragraphs.append("我不会直接给整份答案；下面只给你可迁移的检查路径和局部提示。")
        paragraphs.append(self._next_actions(concepts, workflow_steps, mode))
        return {
            "layer": "L3 交互呈现层",
            "mode": MODE_LABELS.get(mode, mode),
            "style": style_label,
            "prompt_contract": {
                "id": style_prompt["id"] if style_prompt else style_prompt_id,
                "title": style_prompt["title"] if style_prompt else style_label,
                "input": style_prompt["input"] if style_prompt else "L2 聚合策略",
                "output": style_prompt["output"] if style_prompt else "学生可读反馈",
            },
            "answer": "\n\n".join(paragraphs),
            "workflow_steps": workflow_steps,
            "orchestration": orchestration,
            "student_next_step": "按一个最小样例运行并说明变量变化，再回来让系统继续追问或校准图谱。",
        }

    @staticmethod
    def _workflow_steps(workflow: str) -> list[str]:
        if workflow == "adapt":
            return ["A 诊断卡点", "D 选择支架", "A 行动尝试", "P 练习验证", "T 迁移复盘"]
        if workflow == "coder":
            return ["C 情境激活", "O 组织编排", "D 协同开发", "E 循环调试", "R 反思重构"]
        return ["定位问题", "形成伪代码", "局部实现", "测试验证", "反思迁移"]

    @staticmethod
    def _next_actions(concepts: list[str], workflow_steps: list[str], mode: str) -> str:
        concept_line = "、".join(concepts) if concepts else "当前知识点"
        if mode == "daily":
            return f"下一步：先用自己的话解释 {concept_line}，再做一个最小样例验证；如果仍卡住，再切到教学模式让系统按课堂流程展开。"
        return f"下一步：沿“{workflow_steps[0]} -> {workflow_steps[-1]}”推进，先写出 {concept_line} 对应的一句话解释，再补一个输入输出样例。"


class CTGraphMAS:
    def __init__(self, store: Store, kg: KnowledgeGraphService) -> None:
        self.store = store
        self.kg = kg
        self.l1 = L1CognitiveIntegrator()
        self.l2_agents = {
            "P1 问题分解": ProblemDecompositionAgent(),
            "P2 抽象建模": AbstractionModelingAgent(),
            "P3 算法设计": AlgorithmDesignAgent(),
            "P4 调试评价": DebugEvaluationAgent(),
        }
        self.l3 = L3Presenter()
        self.gate = TeachingGate()

    def respond(
        self,
        message: str,
        profile: str = "intermediate",
        style: str = "tutor",
        workflow: str = "coder",
        mode: str = "teaching",
    ) -> dict[str, Any]:
        retrieval = self.kg.retrieve(message, hop=2, low_doc_limit=3)
        diagnosis = self.l1.run(message, profile, workflow, mode, retrieval)
        turns: list[dict[str, Any]] = []
        for agent_name in diagnosis["route"]:
            agent = self.l2_agents.get(agent_name)
            if agent:
                turns.append(agent.run(message, diagnosis, retrieval))
        answer = self.l3.present(message, profile, style, workflow, mode, diagnosis, turns, retrieval)
        gate = self.gate.evaluate(message, answer["answer"], diagnosis)
        if not gate["passed"]:
            answer["answer"] += "\n\n门控调整：这类请求更适合你先补全局部思路；系统只提供检查清单、伪代码和一个最小样例方向。"
        interaction_id = self.store.save_interaction(profile, workflow, style, message, diagnosis, answer, gate)
        return {
            "interaction_id": interaction_id,
            "diagnosis": diagnosis,
            "turns": turns,
            "presentation": answer,
            "gate": gate,
            "retrieval": retrieval,
        }
