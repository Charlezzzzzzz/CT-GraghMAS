# CT-GraphMAS

CT-GraphMAS 是一个面向初中 Python 编程学习的知识图谱增强多智能体辅导系统原型。系统采用纯 Python 标准库后端、SQLite 本地数据库和淡蓝色像素风 Web 前端，围绕三篇论文成果实现了登录流程、角色化导航、学生伴学、教师工作台、知识图谱、语料库、设置页面、管理中心、三层多智能体协同、动态图谱路由、少量相关知识注入、上传语料切分、确定性 embedding、知识图谱回写和反代写教学门控。

## 快速运行

```bash
cd /Users/charleslu/Documents/2025年大学生创新创业训练计划项目/2025大创结题
python3 ct_graphmas_system/main.py --port 8877
```

打开：

```text
http://127.0.0.1:8877
```

演示账号：

| 角色 | 用户名 | 密码 | 可见页面 |
| --- | --- | --- | --- |
| 学生 | `student` | `student123` | 我的首页、日常答疑、教学伴学、知识库、我的图谱、设置页面 |
| 教师 | `teacher` | `teacher123` | 班级总览、教师工作台、通用答疑、教学伴学、知识库、知识图谱、语料库、设置页面 |
| 管理员 | `admin` | `admin123` | 系统总览、管理中心、设置页面、教师视图、知识库、知识图谱、语料库 |

系统不依赖 Flask、FastAPI、PyTorch 或外部大模型 API，适合结题答辩、本地演示和后续工程扩展。若需要接入真实 embedding 模型，只需要替换 `ct_graphmas/embedding.py` 中的 `HashingEmbedder`。

## 已实现功能

- 淡蓝色像素风 Web 界面：参考 Codédex 式学习平台气质，以顶部导航组织多个页面，而不是把所有功能堆在同一页。
- 登录与角色流程：内置学生、教师、管理员三类演示账号，本地 session token 保存在浏览器端；不同角色进入后看到不同导航。
- 总览页：展示系统指标、课堂任务和三篇论文如何进入系统设计。
- 日常答疑页：快速自助问答，只暴露必要图谱相关知识、概念澄清和最小下一步。
- 教学伴学页：支持课堂参数、三层对话、三层日志和相关知识列表；将 ADAPT 或 C-O-D-E-R 映射为 L1-L2-L3 的智能体调度链。
- 教师工作台：展示学情看板、任务编排和最近交互记录。
- 知识图谱页：改为更接近 Neo4j/Bloom 的暗色灵动网络画布，支持节点检索、类型筛选、点击选点、拖拽移动、前置相关节点显示、关系高亮和节点详情查看。
- 知识库页：作为独立页面支持文件上传、相关知识切分、embedding、文档/片段管理，并以图谱方式展示文档、相关知识与知识点的连接。
- 语料库页：上传教学材料并执行相关知识切分、embedding 和图谱回写。
- 设置页面：上下排列多智能体编排与 API 网关配置，支持系统动态分配智能体、日常模式自动锁定标准辅导、相关知识策略和外部模型参数配置。
- 管理中心：展示用户角色和系统边界策略。
- 三层多智能体对话：
  - L1 感知与认知整合中枢：识别任务类型、学生画像、知识节点、风险标记与智能体路由。
  - L2 计算思维教学推理层：P1 问题分解、P2 抽象建模、P3 算法设计、P4 调试评价协同生成支架。
  - L3 交互呈现层：同伴型、启发导师型、严格教练型表达，并执行反代写门控。
- 知识图谱：
  - 内置 CT-GraphMAS 系统层、智能体层、计算思维节点、Python 概念节点、典型错误节点、教学流程节点。
  - 上传语料后自动生成 `document -> related_knowledge -> concept` 边。
  - 对话时采用当前路由子图，不注入完整图谱。
- 语料处理：
  - 支持 `.txt`、`.md`、`.csv`、`.json`、`.docx`。
  - 自动切分、摘要、embedding、相似度检索。
  - 相关知识策略默认取少量高相关片段。
- 教学门控：
  - 识别全盘代写、评价越界和上下文过长等风险。
  - 对高风险请求降级为提示、伪代码、局部检查和测试样例方向。
  - 输出解释准确性、修复选择性、认知适配性、反代写克制四项评分。

## 项目结构

```text
ct_graphmas_system/
├── main.py                         # 本地 Web 服务与 JSON API
├── ct_graphmas/
│   ├── agents.py                   # L1/L2/L3 多智能体与门控
│   ├── chunking.py                 # 教学语料切分
│   ├── embedding.py                # 轻量确定性 embedding
│   ├── knowledge_graph.py          # 图谱入库、动态图谱路由、相关知识检索
│   ├── seed_data.py                # 论文系统内置图谱节点与边
│   ├── storage.py                  # SQLite 数据层
│   ├── textutils.py                # 上传文件解析，含 docx 提取
│   └── theory.py                   # 三篇论文理论模型与系统设计原则
├── static/
│   ├── index.html                  # 像素风系统界面
│   ├── styles.css                  # 像素风样式
│   └── app.js                      # 前端交互与图谱画布
├── data/
│   └── ct_graphmas.sqlite3         # 首次运行后自动生成
└── docs/
    └── 论文可用系统说明.md
```

## API

### 查看语料池

```bash
curl -s http://127.0.0.1:8877/api/corpus
```

### 查看知识图谱

```bash
curl -s http://127.0.0.1:8877/api/graph
```

### 上传语料

```bash
curl -s -X POST http://127.0.0.1:8877/api/upload \
  -H 'Content-Type: application/json' \
  -d '{"filename":"lesson.md","text":"Python 列表索引从 0 开始，调试时应先检查循环边界。"}'
```

### 运行三层对话

```bash
curl -s -X POST http://127.0.0.1:8877/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"我写列表循环时总是 IndexError，怎么定位？","profile":"intermediate","style":"tutor","workflow":"coder"}'
```

## 与论文结论的对应

| 论文结论 | 系统实现 |
| --- | --- |
| 知识图谱提升结构化与可解释性 | `seed_data.py` 内置课程概念、错误模式、智能体和教学流程；上传语料自动回写图谱边 |
| 动态路由优于过深图谱注入 | `KnowledgeGraphService.retrieve()` 围绕当前路由节点扩展相关知识 |
| 少量相关知识优于过多教学文档注入 | 默认只取少量高相关片段 |
| 多智能体应按学情和任务路由 | L1 根据新手/中等/进阶画像选择 P1/P2/P3/P4 组合 |
| 评价强调正确、启发、克制、可用 | `TeachingGate` 输出门控动作和四维评分 |
| 系统要进入教学闭环 | 前端提供学生对话、语料维护、图谱浏览和交互记录入口 |

## 后续扩展点

- 将 `HashingEmbedder` 替换为本地 `bge-small-zh`、`text2vec` 或 OpenAI embedding。
- 增加教师端知识点掌握度编辑，将 `nodes.mastery` 接入课堂记录。
- 增加管理员端账号、班级和权限表。
- 将 L2 智能体模板替换为可配置 prompt 或本地 LLM。
- 接入 NetworkX 或 Neo4j 做更复杂的图谱推理。
