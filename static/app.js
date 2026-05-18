const state = {
  token: localStorage.getItem("ctg_token") || "",
  user: null,
  page: "home",
  graph: { nodes: [], edges: [] },
  corpus: { documents: [], chunk_count: 0, node_count: 0, edge_count: 0 },
  dashboard: { stats: {}, tasks: [], mastery: [], latest_interactions: [] },
  theory: { models: [], principles: [] },
  promptWorkflow: { prompts: [], workflow: [], runtime_design: {} },
  settings: {},
  agentSettings: {},
  users: [],
  graphAnimating: false,
  graphQuery: "",
  graphKind: "",
  selectedGraphNodeId: "",
  graphLayout: new Map(),
  graphManualPositions: {},
  graphDrag: null,
  kbQuery: "",
  kbSelectedId: "",
  kbLayout: new Map(),
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const kindColors = {
  system: "#ff8fa3",
  layer: "#5ca8ff",
  agent: "#ffe17a",
  ct_skill: "#66d9e8",
  python_concept: "#9be7c5",
  error_pattern: "#ff8fa3",
  strategy: "#a8a5ff",
  workflow: "#ffd166",
  guardrail: "#13243d",
  theory: "#d8eeff",
  student_profile: "#b9ddff",
  document: "#ffffff",
  chunk: "#eaf6ff",
  micro_concept: "#d8eeff",
  student_state: "#ffe17a",
};

const DEFAULT_AGENT_SETTINGS = {
  defaultProfile: "intermediate",
  defaultMode: "teaching",
  assignmentPolicy: "dynamic",
  defaultWorkflow: "coder",
  defaultStyle: "tutor",
  evidencePolicy: "route-evidence",
  agentP1: true,
  agentP2: true,
  agentP3: true,
  agentP4: true,
  antiGhostwrite: true,
};

const VALID_EVIDENCE_POLICIES = new Set(["route-evidence", "graph-first", "corpus-first", "minimal"]);

const guideContent = {
  student: {
    eyebrow: "Student Guide",
    title: "学生使用说明",
    body: "你进入系统后，只需要关注自己的学号、班级任务、伴学对话、知识库和个人图谱。系统不会把管理员统计塞给你，而是把教师分配的任务、图谱相关知识和三层智能体提示整理成可操作的下一步。",
    steps: [
      "在登录页使用 student / student123 进入“我的首页”，先确认学号、班级和教师发布的班级任务。",
      "遇到日常小问题时进入“日常答疑”，系统只给必要提示、概念澄清和最小下一步。",
      "完成课堂任务时进入“教学伴学”，选择 C-O-D-E-R、ADAPT 或标准辅导，系统会运行 L1 诊断、L2 多智能体协作和 L3 反馈呈现。",
      "打开“知识库”查看教师上传材料形成的文档、相关知识和图谱连接；打开“我的图谱”检索知识点、错误模式和前置节点。",
      "在“设置页面”调整学习者画像、表达风格和默认模式；API Key 由教师或管理员配置，你不需要自己填写。",
    ],
    screens: [
      {
        src: "/static/assets/guides/student-home.png",
        title: "我的首页",
        caption: "你能看到自己的默认学号、所在班级、班级任务和学习画像，任务只显示教师已经分配到本班的内容。",
      },
      {
        src: "/static/assets/guides/student-answer.png",
        title: "教学伴学回答",
        caption: "输入课堂问题后，系统会给出 L1 诊断、L2 协作结论、相关知识和下一步行动，不直接替你写完整代码。",
      },
      {
        src: "/static/assets/guides/student-graph.png",
        title: "我的图谱",
        caption: "你可以搜索知识点并点击节点，查看它和前置知识、错误模式、相关知识之间的关系。",
      },
    ],
    example: {
      title: "示例提问与回答",
      question: "老师，我写 Python 列表循环时总是下标越界。请按课堂伴学流程提示我下一步，不要直接给完整代码。",
      answer: [
        "L1 诊断：你现在更接近“编程过程与算法组织”卡点，系统会围绕列表与索引、IndexError、循环结构做图谱路由。",
        "L2 协作：P1 先帮你拆输入、循环范围和输出；P3 建议用最小样例检查 range 的终点；P4 提醒你打印 i 与 len(list) 的关系。",
        "L3 下一步：先写一个只有 3 个元素的列表，逐轮记录 i 的值；确认最后一次访问是否超过 len(list)-1，再回来继续调试。",
      ],
    },
    api: {
      title: "真实模型窗口",
      body: "学生端不显示 API Key 输入框。你看到的回答会自动使用教师或管理员在“设置页面 -> 模型 API 设置”中配置好的模型；没有 Key 时，系统使用本地演示智能体生成示例回答。",
    },
  },
  teacher: {
    eyebrow: "Teacher Guide",
    title: "教师使用说明",
    body: "你进入系统后，可以把班级任务、知识库材料、图谱相关知识和多智能体流程组织成一套课堂支架。学生端只接收你分配到其班级的任务，系统回答会保留反代写门控和过程性提示。",
    steps: [
      "使用 teacher / teacher123 登录，先在“班级总览”查看当前班级、学生数量、已分配任务和课堂交互。",
      "进入“教师工作台”，在“班级任务分配”里选择班级、画像、教学流程、截止时间和任务说明。",
      "发布状态选择“已分配”时，学生会在“我的班级任务”中看到；选择“待发布”或“草稿”时，任务只留在你的任务编排区。",
      "进入“知识库”上传教学材料，系统会自动切分、embedding，并把文档、相关知识和知识点连成图谱。",
      "进入“设置页面”配置默认教学模式、多智能体分配策略和模型 API；你可以先保留本地演示，等 Key 准备好后再启用真实模型。",
    ],
    screens: [
      {
        src: "/static/assets/guides/teacher-home.png",
        title: "班级总览",
        caption: "你可以看到任教班级、班级学生、已分配任务、待发布任务、语料文档和课堂交互。",
      },
      {
        src: "/static/assets/guides/teacher-workbench.png",
        title: "教师工作台",
        caption: "这里负责班级任务分配、学情看板、任务编排和最近交互记录，是你控制课堂流程的主入口。",
      },
      {
        src: "/static/assets/guides/teacher-knowledge.png",
        title: "知识库管理",
        caption: "上传课件、讲义或案例后，系统会生成相关知识、embedding 和知识库图谱，后续回答会引用这些内容。",
      },
    ],
    example: {
      title: "示例任务与回答",
      question: "请给八年级 Python 实验班分配“列表条件筛选小项目”，采用 C-O-D-E-R 流程，要求学生不要直接生成完整代码。",
      answer: [
        "任务进入班级任务池后，学生首页只显示“已分配”的本班任务。",
        "学生提问时，L1 会诊断其卡点属于需求澄清、抽象建模、算法设计还是调试评价。",
        "L2 会按路由动态选择 P1/P2/P3/P4，L3 输出提示、伪代码框架、测试样例和反思问题，避免完整代写。",
      ],
    },
    api: {
      title: "给你保留的 API 配置窗口",
      body: "你可以进入“设置页面 -> 模型 API 设置”，填写服务提供方、Base URL、API Key、对话模型、Embedding 模型和 Temperature。填好后勾选“启用外部 API”，系统后续即可替换本地演示回答。",
    },
  },
  admin: {
    eyebrow: "Admin Guide",
    title: "管理员说明",
    body: "你进入系统后，负责维护账号角色、API 接入、知识图谱边界、反代写门控和系统运行策略。管理员视角会保留全局数据，但说明文字会直接告诉你该做什么，而不是第三者介绍系统。",
    steps: [
      "使用 admin / admin123 登录，进入“系统总览”查看全局用户、任务、知识库、图谱和交互情况。",
      "进入“管理中心”检查用户角色、系统边界、反代写门控、相关知识边界和教师监督机制。",
      "进入“设置页面”配置多智能体策略和 API；真实模型接入前可继续使用本地演示智能体。",
      "进入“知识图谱”检索节点、拖动布局、查看前置相关节点，并检查文档相关知识是否和知识点正确连接。",
      "当你准备好 Key 后，在模型 API 设置窗口填写并启用外部 API；不要把 Key 写进代码或截图里。",
    ],
    screens: [
      {
        src: "/static/assets/guides/admin-center.png",
        title: "管理中心",
        caption: "你可以检查用户与角色、反代写门控、相关知识边界、语料注入和教师可监督策略。",
      },
      {
        src: "/static/assets/guides/admin-settings.png",
        title: "设置页面",
        caption: "这里包含多智能体配置和模型 API 设置，是保留给你填 Key、切模型、换 embedding 的正式窗口。",
      },
      {
        src: "/static/assets/guides/admin-graph.png",
        title: "知识图谱",
        caption: "你可以查看系统层、智能体层、计算思维知识点、错误模式和相关知识的关系是否完整。",
      },
    ],
    example: {
      title: "示例配置与输出",
      question: "我已经配置 OpenAI-compatible 网关，希望系统用真实模型生成 L2 智能体回答，同时保留反代写门控。",
      answer: [
        "API 设置启用后，L2 智能体生成可以接入真实模型，Embedding 也可以替换为配置的 embedding 模型。",
        "系统仍会先做 L1 诊断和图谱路由，再把必要相关知识传给模型，避免回答脱离课堂任务和知识库。",
        "最终回答继续经过反代写门控，只输出提示、局部思路、测试样例和复盘问题，不直接交付完整代码。",
      ],
    },
    api: {
      title: "给你保留的 Key 输入窗口",
      body: "设置页面的“模型 API 设置”就是给你预留的窗口。你填入 API Key 后，保存并启用即可；数据库只保存本地配置，界面再次读取时会以掩码显示 Key。",
    },
  },
};

const navByRole = {
  student: [
    { id: "home", label: "我的首页" },
    { id: "daily", label: "日常答疑" },
    { id: "teaching", label: "教学伴学" },
    { id: "knowledge", label: "知识库" },
    { id: "graph", label: "我的图谱" },
    { id: "settings", label: "设置页面" },
  ],
  teacher: [
    { id: "home", label: "班级总览" },
    { id: "teacher", label: "教师工作台" },
    { id: "daily", label: "通用答疑" },
    { id: "teaching", label: "教学伴学" },
    { id: "knowledge", label: "知识库" },
    { id: "graph", label: "知识图谱" },
    { id: "corpus", label: "语料库" },
    { id: "settings", label: "设置页面" },
  ],
  admin: [
    { id: "home", label: "系统总览" },
    { id: "admin", label: "管理中心" },
    { id: "settings", label: "设置页面" },
    { id: "teacher", label: "教师视图" },
    { id: "knowledge", label: "知识库" },
    { id: "graph", label: "知识图谱" },
    { id: "corpus", label: "语料库" },
  ],
};

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDisplayName(text) {
  return String(text || "").replaceAll("陆" + "同学", "L同学");
}

const profileLabels = {
  novice: "破冰期",
  intermediate: "建构期",
  advanced: "自动化期",
  teacher: "教师",
  admin: "管理员",
};

const workflowLabels = {
  coder: "C-O-D-E-R",
  adapt: "ADAPT",
  standard: "标准辅导",
};

const kindLabels = {
  chunk: "相关知识",
  document: "文档",
  micro_concept: "Python微观考点",
  student_state: "学情画像",
  student_profile: "学习者画像",
  python_concept: "Python知识点",
  ct_skill: "计算思维",
  error_pattern: "错误模式",
};

const relationLabels = {
  HAS_CHUNK: "包含相关知识",
  MENTIONS: "关联知识点",
  KNOWS: "学情掌握",
  REQUIRES: "需要前置",
  PREREQUISITE_OF: "前置于",
};

function displayKind(kind) {
  return kindLabels[kind] || kind || "";
}

function displayRelation(relation) {
  return relationLabels[relation] || relation || "";
}

function defaultStudentNo(user = {}) {
  if (user.student_no) return user.student_no;
  const id = Number(user.id || 1);
  return `S2025${String(id).padStart(3, "0")}`;
}

function shortClassName(className = "") {
  return String(className || "默认班级").replace(/\s+/g, " ").trim();
}

function sameClass(task, user) {
  const taskClass = String(task.class_name || "").trim();
  const userClass = String(user?.class_name || "").trim();
  return !taskClass || !userClass || taskClass === userClass;
}

function publishedForStudents(task) {
  return ["已分配", "进行中"].includes(task.status);
}

function studentVisibleTasks(tasks = []) {
  return tasks.filter((task) => sameClass(task, state.user) && publishedForStudents(task));
}

function teacherClassTasks(tasks = []) {
  return tasks.filter((task) => sameClass(task, state.user));
}

function loadAgentSettings() {
  try {
    const parsed = JSON.parse(localStorage.getItem("ctg_agent_settings") || "{}");
    const settings = { ...DEFAULT_AGENT_SETTINGS, ...parsed };
    if (!VALID_EVIDENCE_POLICIES.has(settings.evidencePolicy)) settings.evidencePolicy = "route-evidence";
    if (settings.defaultMode === "daily") settings.defaultWorkflow = "standard";
    return settings;
  } catch (_) {
    return { ...DEFAULT_AGENT_SETTINGS };
  }
}

state.agentSettings = loadAgentSettings();

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function showLogin() {
  $("#loginView").classList.remove("hidden");
  $("#appView").classList.add("hidden");
}

function showApp() {
  $("#loginView").classList.add("hidden");
  $("#appView").classList.remove("hidden");
}

async function handleLogin(event) {
  event.preventDefault();
  $("#loginStatus").textContent = "正在登录…";
  try {
    const data = await api("/api/login", {
      method: "POST",
      body: JSON.stringify({
        username: $("#loginUsername").value.trim(),
        password: $("#loginPassword").value,
      }),
    });
    state.token = data.token;
    state.user = data.user;
    localStorage.setItem("ctg_token", state.token);
    showApp();
    await hydrate();
    navigate("home");
  } catch (error) {
    $("#loginStatus").textContent = error.message;
  }
}

async function logout() {
  try {
    await api("/api/logout", { method: "POST", body: "{}" });
  } catch (_) {
    // Local demo logout should still clear the browser session.
  }
  state.token = "";
  state.user = null;
  localStorage.removeItem("ctg_token");
  showLogin();
}

async function checkSession() {
  if (!state.token) {
    showLogin();
    return;
  }
  try {
    const data = await api("/api/session");
    if (!data.user) throw new Error("session expired");
    state.user = data.user;
    showApp();
    await hydrate();
    navigate("home");
  } catch (_) {
    state.token = "";
    localStorage.removeItem("ctg_token");
    showLogin();
  }
}

async function hydrate() {
  const [corpus, graph, dashboard, theory, promptWorkflow, users, settings] = await Promise.all([
    api("/api/corpus"),
    api("/api/graph"),
    api("/api/dashboard"),
    api("/api/theory"),
    api("/api/prompt-workflow"),
    api("/api/users"),
    api("/api/settings"),
  ]);
  state.corpus = corpus;
  state.graph = graph;
  state.dashboard = dashboard;
  state.theory = theory;
  state.promptWorkflow = promptWorkflow;
  state.users = users.users || [];
  state.settings = settings.settings || {};
  renderShell();
  renderAll();
}

function renderShell() {
  const user = state.user || {};
  $("#userName").textContent = formatDisplayName(user.display_name || "未登录");
  if (user.role === "student") {
    $("#userRole").textContent = `${defaultStudentNo(user)} · ${user.class_name || "默认班级"}`;
  } else if (user.role === "teacher") {
    $("#userRole").textContent = `${user.class_name || "默认班级"} · 教师`;
  } else {
    $("#userRole").textContent = `${user.role || "guest"} · ${user.class_name || "本地演示"}`;
  }
  $("#userAvatar").textContent = user.avatar || "CT";

  const nav = navByRole[user.role] || navByRole.student;
  $("#topNav").innerHTML = nav
    .map((item) => `<button class="nav-tab" data-page="${item.id}" type="button">${escapeHtml(item.label)}</button>`)
    .join("");
  $$(".nav-tab").forEach((button) => {
    button.onclick = () => navigate(button.dataset.page);
  });
  $$(".nav-jump").forEach((button) => {
    button.onclick = () => navigate(button.dataset.target);
  });
}

function navigate(page) {
  if (!page) return;
  const allowed = new Set((navByRole[state.user?.role] || navByRole.student).map((item) => item.id));
  if (!allowed.has(page)) page = "home";
  state.page = page;
  $$(".page").forEach((section) => section.classList.toggle("active", section.dataset.page === page));
  $$(".nav-tab").forEach((button) => button.classList.toggle("active", button.dataset.page === page));
  if (page === "graph") {
    startGraphAnimation();
  } else if (page === "knowledge") {
    state.graphAnimating = false;
    drawKnowledgeGraph();
  } else {
    state.graphAnimating = false;
  }
}

function renderAll() {
  renderStats();
  renderTasks();
  renderTheory();
  renderDocs();
  renderTeacher();
  renderUsers();
  renderSettings();
  renderAgentSettings();
  renderPromptWorkflow();
  renderGraphSummary();
  renderGraphFilters();
  renderGraphResults();
  renderKnowledgeBase();
  renderRoleCopy();
  renderModeInfo();
  drawGraph();
  renderLegend();
}

function renderRoleCopy() {
  const role = state.user?.role || "student";
  const hero = document.querySelector(".hero-band h2");
  const text = document.querySelector(".hero-band p:not(.eyebrow)");
  if (!hero || !text) return;
  if (role === "teacher") {
    hero.textContent = "把多智能体支架编排进你的课堂";
    text.textContent = "你可以从班级任务、学情差异、语料维护和图谱校准入手，把 ADAPT 与 C-O-D-E-R 变成可发布、可观察、可复盘的课堂调度规则。";
  } else if (role === "admin") {
    hero.textContent = "维护可追溯、可监督、可扩展的教学智能系统";
    text.textContent = "你可以管理账号角色、数据闭环、知识图谱边界和反代写策略，让系统能力始终服务教学目标，而不是滑向无限制代码生成。";
  } else {
    hero.textContent = "从“问答案”走向“会思考”的编程伴学";
    text.textContent = "你可以在日常通用模式中快速获得必要提示，也可以在教学模式中沿 ADAPT 或 C-O-D-E-R 流程完成问题分解、抽象建模、算法设计和调试复盘。";
  }
}

function renderModeInfo() {
  const mode = $("#assistMode")?.value || "teaching";
  const workflow = $("#workflow")?.value || "coder";
  const info = $("#modeInfo");
  if (!info) return;
  if (mode === "daily") {
    info.textContent = "日常通用模式：保留必要图谱相关知识，但只给必要提示、概念澄清和最小下一步。";
  } else if (workflow === "adapt") {
    info.textContent = "教学模式 + ADAPT：L1 诊断卡点，L2 选择支架，L3 给行动、练习与迁移复盘。";
  } else {
    info.textContent = "教学模式 + C-O-D-E-R：情境激活由 P1 承接，协同开发由 P2/P3 承接，循环调试由 P4 承接。";
  }
}

function renderStats() {
  const stats = state.dashboard.stats || {};
  const tasks = state.dashboard.tasks || [];
  const role = state.user?.role || "student";
  let cards;

  if (role === "student") {
    const visibleTasks = studentVisibleTasks(tasks);
    cards = [
      { value: defaultStudentNo(state.user), label: "我的学号" },
      { value: shortClassName(state.user?.class_name), label: "我的班级" },
      { value: visibleTasks.length, label: "班级任务" },
      { value: profileLabels[state.user?.profile] || "建构期", label: "学习画像" },
      { value: Number(stats.documents || 0), label: "知识库文档" },
      { value: Number(stats.nodes || 0), label: "图谱节点" },
      { value: Number(stats.interactions || 0), label: "学习交互" },
    ];
  } else if (role === "teacher") {
    const classTasks = teacherClassTasks(tasks);
    const classStudents = (state.users || []).filter((user) => user.role === "student" && sameClass({ class_name: user.class_name }, state.user)).length;
    cards = [
      { value: shortClassName(state.user?.class_name), label: "任教班级" },
      { value: classStudents, label: "班级学生" },
      { value: classTasks.filter(publishedForStudents).length, label: "已分配任务" },
      { value: classTasks.filter((task) => task.status === "待发布").length, label: "待发布任务" },
      { value: Number(stats.documents || 0), label: "语料文档" },
      { value: Number(stats.nodes || 0), label: "图谱节点" },
      { value: Number(stats.interactions || 0), label: "课堂交互" },
    ];
  } else {
    cards = [
      { value: Number(stats.users || 0), label: "用户" },
      { value: Number(stats.tasks || 0), label: "任务" },
      { value: Number(stats.documents || 0), label: "文档" },
      { value: Number(stats.chunks || 0), label: "相关知识条目" },
      { value: Number(stats.nodes || 0), label: "图谱节点" },
      { value: Number(stats.edges || 0), label: "图谱关系" },
      { value: Number(stats.interactions || 0), label: "交互" },
    ];
  }

  $("#statGrid").innerHTML = cards
    .map((card) => {
      const value = String(card.value ?? "0");
      const compact = value.length > 7 ? " stat-card--text" : "";
      return `<article class="stat-card${compact}"><b>${escapeHtml(value)}</b><span>${escapeHtml(card.label)}</span></article>`;
    })
    .join("");
}

function renderTaskCards(tasks, emptyText, options = {}) {
  return tasks.length
    ? tasks
        .map((task) => {
          const meta = [
            workflowLabels[task.workflow] || String(task.workflow || "").toUpperCase(),
            profileLabels[task.target_profile] || "全班",
            task.status,
            task.due_label || "未设置",
          ];
          if (options.showClass) meta.push(task.class_name || "未指定班级");
          if (options.showTeacher && task.assigned_by) meta.push(`发布：${formatDisplayName(task.assigned_by)}`);
          return `<article class="task-card">
            <strong>${escapeHtml(task.title)}</strong>
            <span>${meta.filter(Boolean).map(escapeHtml).join(" · ")}</span>
            <p>${escapeHtml(task.description)}</p>
          </article>`;
        })
        .join("")
    : `<div class="empty">${escapeHtml(emptyText)}</div>`;
}

function renderTasks() {
  const tasks = state.dashboard.tasks || [];
  const role = state.user?.role || "student";
  const homeTitle = $("#homeTaskTitle");
  const homeButton = $("#homeTaskButton");
  let homeTasks = tasks;
  let homeEmpty = "暂无任务";

  if (role === "student") {
    homeTasks = studentVisibleTasks(tasks);
    homeEmpty = "你当前还没有教师发布到本班的任务。";
    if (homeTitle) homeTitle.textContent = "我的班级任务";
    if (homeButton) {
      homeButton.textContent = "进入伴学";
      homeButton.dataset.target = "teaching";
    }
  } else if (role === "teacher") {
    homeTasks = teacherClassTasks(tasks);
    homeEmpty = "你还没有给当前班级发布任务。";
    if (homeTitle) homeTitle.textContent = "班级任务";
    if (homeButton) {
      homeButton.textContent = "进入工作台";
      homeButton.dataset.target = "teacher";
    }
  } else {
    if (homeTitle) homeTitle.textContent = "系统任务";
    if (homeButton) {
      homeButton.textContent = "进入管理";
      homeButton.dataset.target = "admin";
    }
  }

  $("#homeTaskList").innerHTML = renderTaskCards(homeTasks, homeEmpty, {
    showClass: role !== "student",
    showTeacher: role === "student",
  });
  $("#teacherTaskList").innerHTML = renderTaskCards(teacherClassTasks(tasks), "当前班级暂无任务，请先在左侧分配。", {
    showClass: true,
    showTeacher: true,
  });
}

function renderTheory() {
  const models = state.theory.models || [];
  if ($("#homeTheoryList")) {
    $("#homeTheoryList").innerHTML = models
      .map(
        (model) => `<article class="theory-mini">
          <strong>${escapeHtml(model.title)}</strong>
          <span>${escapeHtml(model.tagline)}</span>
        </article>`,
      )
      .join("");
  }
  if (!$("#theoryModels") || !$("#principleGrid")) return;
  $("#theoryModels").innerHTML = models
    .map(
      (model) => `<article class="theory-card pixel-card">
        <p class="eyebrow">${escapeHtml(model.paper)}</p>
        <h3>${escapeHtml(model.title)}</h3>
        <p class="muted">${escapeHtml(model.tagline)}</p>
        <div class="stage-list">
          ${(model.stages || [])
            .map(
              (stage) => `<div class="stage">
                <b>${escapeHtml(stage.key)}</b>
                <div>
                  <strong>${escapeHtml(stage.label)}</strong>
                  <span>${escapeHtml(stage.name)} · ${escapeHtml(stage.detail)}</span>
                </div>
              </div>`,
            )
            .join("")}
        </div>
        <div class="hook-list">
          ${(model.system_hooks || []).map((hook) => `<span>${escapeHtml(hook)}</span>`).join("")}
        </div>
      </article>`,
    )
    .join("");
  $("#principleGrid").innerHTML = (state.theory.principles || [])
    .map(
      (item) => `<article class="principle-card pixel-card">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.body)}</p>
      </article>`,
    )
    .join("");
}

function renderDocs() {
  const docs = state.corpus.documents || [];
  $("#docList").innerHTML =
    docs.length === 0
      ? '<div class="empty">暂无上传文档</div>'
      : docs
          .map(
            (doc) => `<article class="doc-item">
              <strong>${escapeHtml(doc.title || doc.filename)}</strong>
              <span>${doc.chunks} 条相关知识 · ${escapeHtml(doc.source_type)} · ${escapeHtml(doc.created_at)}</span>
            </article>`,
          )
          .join("");
}

function knowledgeGraphData() {
  const nodeById = new Map((state.graph.nodes || []).map((node) => [node.id, node]));
  const ids = new Set();
  const edges = [];
  (state.graph.edges || []).forEach((edge) => {
    const source = nodeById.get(edge.source);
    const target = nodeById.get(edge.target);
    const isKnowledgeEdge =
      edge.relation === "HAS_CHUNK" ||
      (edge.relation === "MENTIONS" && source?.kind === "chunk") ||
      source?.kind === "document" ||
      source?.kind === "chunk" ||
      target?.kind === "document" ||
      target?.kind === "chunk";
    if (!isKnowledgeEdge) return;
    ids.add(edge.source);
    ids.add(edge.target);
    edges.push(edge);
  });
  const query = state.kbQuery.trim().toLowerCase();
  let nodes = [...ids].map((id) => nodeById.get(id)).filter(Boolean);
  if (query) {
    const matched = new Set(
      nodes
        .filter((node) => graphNodeText(node).includes(query))
        .map((node) => node.id),
    );
    edges.forEach((edge) => {
      if (matched.has(edge.source)) matched.add(edge.target);
      if (matched.has(edge.target)) matched.add(edge.source);
    });
    nodes = nodes.filter((node) => matched.has(node.id));
  }
  const visible = new Set(nodes.map((node) => node.id));
  return {
    nodes,
    edges: edges.filter((edge) => visible.has(edge.source) && visible.has(edge.target)),
  };
}

function renderKnowledgeBase() {
  if (!$("#kbDocList")) return;
  const docs = state.corpus.documents || [];
  $("#kbCorpusStats").innerHTML = `
    <article><b>${Number(state.corpus.document_count || docs.length || 0)}</b><span>文档</span></article>
    <article><b>${Number(state.corpus.chunk_count || 0)}</b><span>相关知识</span></article>
    <article><b>128d</b><span>Hashing Embedding</span></article>
  `;
  $("#kbDocList").innerHTML =
    docs.length === 0
      ? '<div class="empty">你还没有上传文档</div>'
      : docs
          .map(
            (doc) => `<button class="kb-doc-item" data-node-id="doc:${doc.id}" type="button">
              <strong>${escapeHtml(doc.title || doc.filename)}</strong>
              <span>${doc.chunks} 条相关知识 · ${escapeHtml(doc.source_type)} · ${escapeHtml(doc.created_at)}</span>
            </button>`,
          )
          .join("");
  $$(".kb-doc-item").forEach((button) => {
    button.onclick = () => selectKnowledgeNode(button.dataset.nodeId);
  });
  renderKnowledgeSelection();
  drawKnowledgeGraph();
}

function renderKnowledgeSelection() {
  const target = $("#kbSelected");
  if (!target) return;
  const data = knowledgeGraphData();
  const selected = data.nodes.find((node) => node.id === state.kbSelectedId);
  if (!selected) {
    target.innerHTML = '<div class="empty">点击知识库图谱中的文档、相关知识或知识点查看详情</div>';
    return;
  }
  const related = data.edges.filter((edge) => edge.source === selected.id || edge.target === selected.id).slice(0, 10);
  target.innerHTML = `<article class="graph-selected-card">
    <strong>${escapeHtml(selected.label)}</strong>
    <span>${escapeHtml(displayKind(selected.kind))}</span>
    <p>${escapeHtml(selected.description || "暂无描述")}</p>
    <div class="graph-relation-list">
      ${
        related.length
          ? related
              .map((edge) => {
                const otherId = edge.source === selected.id ? edge.target : edge.source;
                const other = data.nodes.find((node) => node.id === otherId);
                return `<button class="graph-relation" data-node-id="${escapeHtml(otherId)}" type="button">
                  ${escapeHtml(displayRelation(edge.relation))} → ${escapeHtml(other?.label || otherId)}
                </button>`;
              })
              .join("")
          : '<span class="empty">暂无知识库关系</span>'
      }
    </div>
  </article>`;
  $$("#kbSelected .graph-relation").forEach((button) => {
    button.onclick = () => selectKnowledgeNode(button.dataset.nodeId);
  });
}

function kbNodePosition(node, index, width, height) {
  const tiers = { document: 0.18, chunk: 0.5 };
  const xRatio = tiers[node.kind] ?? 0.82;
  const seed = hashNumber(node.id);
  const band = 54 + ((seed + index * 41) % Math.max(80, Math.floor(height - 108)));
  return {
    x: width * xRatio + Math.sin(seed) * 18,
    y: band,
  };
}

function drawKnowledgeGraph() {
  const canvas = $("#kbGraphCanvas");
  if (!canvas) return;
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  canvas.width = Math.max(360, Math.floor(rect.width * ratio));
  canvas.height = Math.max(300, Math.floor(rect.height * ratio));
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  const data = knowledgeGraphData();
  const nodeMap = new Map();
  data.nodes.forEach((node, index) => {
    nodeMap.set(node.id, { ...node, ...kbNodePosition(node, index, width, height) });
  });
  state.kbLayout = nodeMap;

  ctx.clearRect(0, 0, width, height);
  const bg = ctx.createLinearGradient(0, 0, width, height);
  bg.addColorStop(0, "#071421");
  bg.addColorStop(1, "#0f3154");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);

  data.edges.forEach((edge) => {
    const source = nodeMap.get(edge.source);
    const target = nodeMap.get(edge.target);
    if (!source || !target) return;
    const selected = edge.source === state.kbSelectedId || edge.target === state.kbSelectedId;
    ctx.strokeStyle = selected ? "rgba(255,225,122,0.86)" : edge.relation === "HAS_CHUNK" ? "rgba(92,168,255,0.42)" : "rgba(102,217,232,0.46)";
    ctx.lineWidth = selected ? 3 : 1.8;
    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    ctx.bezierCurveTo((source.x + target.x) / 2, source.y, (source.x + target.x) / 2, target.y, target.x, target.y);
    ctx.stroke();
  });

  nodeMap.forEach((node) => {
    const selected = node.id === state.kbSelectedId;
    const color = node.kind === "document" ? "#ffe17a" : node.kind === "chunk" ? "#66d9e8" : kindColors[node.kind] || "#ffffff";
    const size = node.kind === "document" ? 17 : node.kind === "chunk" ? 12 : 10;
    ctx.save();
    ctx.shadowColor = color;
    ctx.shadowBlur = selected ? 28 : 14;
    ctx.beginPath();
    ctx.arc(node.x, node.y, selected ? size + 5 : size, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.lineWidth = selected ? 4 : 2;
    ctx.strokeStyle = selected ? "#ffffff" : "rgba(255,255,255,0.82)";
    ctx.stroke();
    ctx.restore();
    ctx.font = '12px "Courier New", monospace';
    ctx.fillStyle = selected ? "#ffe17a" : "rgba(236,248,255,0.9)";
    const label = node.label.length > 14 ? `${node.label.slice(0, 14)}…` : node.label;
    ctx.fillText(label, node.x + 14, node.y - 8);
  });

  const status = $("#kbGraphStatus");
  if (status) status.textContent = `知识库图谱当前显示 ${data.nodes.length} 个节点、${data.edges.length} 条关系。`;
}

function selectKnowledgeNode(nodeId) {
  if (!nodeId) return;
  state.kbSelectedId = nodeId;
  renderKnowledgeSelection();
  drawKnowledgeGraph();
}

function handleKnowledgeCanvasClick(event) {
  if (!state.kbLayout?.size) return;
  const canvas = $("#kbGraphCanvas");
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  let nearest = null;
  let distance = Infinity;
  state.kbLayout.forEach((node) => {
    const d = Math.hypot(node.x - x, node.y - y);
    if (d < distance) {
      nearest = node;
      distance = d;
    }
  });
  if (nearest && distance <= 30) selectKnowledgeNode(nearest.id);
}

function renderTeacher() {
  $("#masteryList").innerHTML = (state.dashboard.mastery || [])
    .map(
      (item) => `<div class="mastery-row">
        <div class="mastery-meta"><strong>${escapeHtml(item.label)}</strong><span>${Math.round(item.value * 100)}% ${escapeHtml(item.trend)}</span></div>
        <div class="bar"><i style="width:${Math.round(item.value * 100)}%"></i></div>
      </div>`,
    )
    .join("");

  if ($("#assignmentClass") && !$("#assignmentClass").value.trim()) {
    $("#assignmentClass").value = state.user?.class_name || "八年级 Python 实验班";
  }

  const interactions = state.dashboard.latest_interactions || [];
  $("#interactionList").innerHTML =
    interactions.length === 0
      ? '<div class="empty">暂无交互记录</div>'
      : interactions
          .map((row) => {
            const diagnosis = row.diagnosis_json || {};
            const gate = row.gate_json || {};
            return `<article class="interaction-card">
              <strong>#${row.id} ${escapeHtml(diagnosis.task_type || "编程辅导")}</strong>
              <span>${escapeHtml(row.created_at)} · ${escapeHtml(row.workflow)} · ${gate.passed ? "门控通过" : "已调整"}</span>
              <p>${escapeHtml(row.user_message)}</p>
            </article>`;
          })
          .join("");
}

function renderUsers() {
  $("#userTable").innerHTML = (state.users || [])
    .map(
      (user) => {
        const meta = [user.username, user.role === "student" ? defaultStudentNo(user) : "", user.class_name]
          .filter(Boolean)
          .join(" · ");
        return `<article class="user-row">
          <div>
            <strong>${escapeHtml(formatDisplayName(user.display_name))}</strong>
            <span>${escapeHtml(meta)}</span>
          </div>
          <b class="role-pill">${escapeHtml(user.role)}</b>
        </article>`;
      },
    )
    .join("");
}

function renderSettings() {
  if (!$("#settingsForm")) return;
  const settings = state.settings || {};
  $("#apiProvider").value = settings.provider || "local-demo";
  $("#apiBaseUrl").value = settings.base_url || "";
  $("#apiKey").value = settings.api_key || "";
  $("#chatModel").value = settings.chat_model || "";
  $("#embeddingModel").value = settings.embedding_model || "";
  $("#temperature").value = settings.temperature ?? 0.3;
  $("#apiEnabled").checked = Boolean(settings.enabled);
  $("#settingsStatus").textContent = settings.updated_at
    ? `当前配置更新时间：${settings.updated_at}`
    : "设置仅保存在本地 SQLite 中。";
}

function applyAgentSettingsToChat() {
  const settings = state.agentSettings || DEFAULT_AGENT_SETTINGS;
  const workflow = settings.defaultMode === "daily" ? "standard" : settings.defaultWorkflow || "coder";
  if ($("#workflow")) $("#workflow").value = workflow;
  if ($("#style")) $("#style").value = settings.defaultStyle || "tutor";
  if ($("#dailyStyle")) $("#dailyStyle").value = settings.defaultStyle || "tutor";
  renderModeInfo();
}

function syncWorkflowAvailability() {
  if (!$("#defaultMode") || !$("#defaultWorkflow")) return;
  const isDaily = $("#defaultMode").value === "daily";
  $("#defaultWorkflow").value = isDaily ? "standard" : $("#defaultWorkflow").value || "coder";
  $("#defaultWorkflow").disabled = isDaily;
  $("#defaultWorkflow").closest("label")?.classList.toggle("disabled-field", isDaily);
  if ($("#agentSettingsStatus") && isDaily) {
    $("#agentSettingsStatus").textContent = "日常通用模式已固定为标准辅导，不再绑定 ADAPT 或 C-O-D-E-R 教学流程。";
  }
}

function syncAgentAllocationFields() {
  if (!$("#assignmentPolicy")) return;
  const isDynamic = $("#assignmentPolicy").value === "dynamic";
  ["#agentP1", "#agentP2", "#agentP3", "#agentP4"].forEach((selector) => {
    const checkbox = $(selector);
    if (!checkbox) return;
    if (isDynamic) checkbox.checked = true;
    checkbox.disabled = isDynamic;
    checkbox.closest("label")?.classList.toggle("disabled-field", isDynamic);
  });
}

function renderAgentSettings() {
  if (!$("#agentSettingsForm")) return;
  const settings = state.agentSettings || DEFAULT_AGENT_SETTINGS;
  if (!VALID_EVIDENCE_POLICIES.has(settings.evidencePolicy)) settings.evidencePolicy = "route-evidence";
  if (settings.defaultMode === "daily") settings.defaultWorkflow = "standard";
  $("#defaultProfile").value = settings.defaultProfile || "intermediate";
  $("#defaultMode").value = settings.defaultMode || "teaching";
  $("#assignmentPolicy").value = settings.assignmentPolicy || "dynamic";
  $("#defaultWorkflow").value = settings.defaultWorkflow || "coder";
  $("#defaultStyle").value = settings.defaultStyle || "tutor";
  $("#evidencePolicy").value = settings.evidencePolicy || "route-evidence";
  $("#agentP1").checked = Boolean(settings.agentP1);
  $("#agentP2").checked = Boolean(settings.agentP2);
  $("#agentP3").checked = Boolean(settings.agentP3);
  $("#agentP4").checked = Boolean(settings.agentP4);
  $("#antiGhostwrite").checked = Boolean(settings.antiGhostwrite);
  syncWorkflowAvailability();
  syncAgentAllocationFields();
  $("#agentSettingsStatus").textContent =
    `当前预设：${$("#defaultProfile").selectedOptions[0]?.textContent || "建构期中等生"} · ${settings.defaultMode === "daily" ? "日常通用" : "教学模式"} · ${settings.assignmentPolicy === "dynamic" ? "系统动态分配" : "手动指定"} · ${(settings.defaultWorkflow || "coder").toUpperCase()} · ${settings.evidencePolicy || "route-evidence"}`;
  applyAgentSettingsToChat();
}

function renderPromptWorkflow() {
  if (!$("#promptWorkflowList")) return;
  const payload = state.promptWorkflow || {};
  const runtime = payload.runtime_design || {};
  const workflow = payload.workflow || [];
  const prompts = payload.prompts || [];
  $("#runtimeDesign").innerHTML = Object.entries(runtime)
    .map(([key, value]) => `<article>
      <b>${escapeHtml(runtimeLabel(key))}</b>
      <span>${escapeHtml(value)}</span>
    </article>`)
    .join("");
  $("#workflowTimeline").innerHTML = workflow
    .map(
      (step, index) => `<article>
        <b>${index + 1}</b>
        <div>
          <strong>${escapeHtml(step.label)}</strong>
          <span>${escapeHtml(step.description)}</span>
        </div>
      </article>`,
    )
    .join("");
  $("#promptWorkflowList").innerHTML = prompts
    .map(
      (prompt) => `<details class="prompt-row">
        <summary>
          <b>${escapeHtml(prompt.title)}</b>
          <span>${escapeHtml(prompt.role)} · 输入：${escapeHtml(prompt.input)} · 输出：${escapeHtml(prompt.output)}</span>
        </summary>
        <pre>${escapeHtml(prompt.prompt)}</pre>
      </details>`,
    )
    .join("");
}

function runtimeLabel(key) {
  return {
    api_isolation: "API 隔离",
    model_mode: "模型运行",
    kg_mode: "图谱上下文",
    routing_mode: "动态路由",
    mode_binding: "模式绑定",
  }[key] || key;
}

function graphNodeText(node) {
  return `${node.label || ""} ${node.kind || ""} ${node.description || ""} ${node.id || ""}`.toLowerCase();
}

function graphMatches(node) {
  const query = state.graphQuery.trim().toLowerCase();
  const kindOk = !state.graphKind || node.kind === state.graphKind;
  const queryOk = !query || graphNodeText(node).includes(query);
  return kindOk && queryOk;
}

function graphSearchMatches() {
  return (state.graph.nodes || []).filter(graphMatches);
}

function graphPrerequisiteEdges(nodeId) {
  if (!nodeId) return [];
  const incoming = (state.graph.edges || []).filter((edge) => edge.target === nodeId);
  const outgoingRequires = (state.graph.edges || []).filter((edge) => edge.source === nodeId && edge.relation === "REQUIRES");
  const preferred = incoming.filter((edge) =>
    ["PREREQUISITE_OF", "SCAFFOLDS", "GROUNDS", "HAS_CHUNK", "MENTIONS", "ORGANIZES", "KNOWS"].includes(edge.relation),
  );
  return [...outgoingRequires, ...(preferred.length ? preferred : incoming)].slice(0, 12);
}

function graphEdgeOtherId(edge, nodeId) {
  if (edge.relation === "REQUIRES" && edge.source === nodeId) return edge.target;
  return edge.source === nodeId ? edge.target : edge.source;
}

function graphMasteryForNode(nodeId) {
  const edge = (state.graph.edges || []).find((item) => item.target === nodeId && item.relation === "KNOWS");
  if (!edge) return null;
  const student = (state.graph.nodes || []).find((node) => node.id === edge.source);
  const meta = edge.meta || {};
  return {
    student: student?.label || "建构期中等生",
    mastery: Number(meta.mastery_level ?? edge.weight ?? 0),
    errors: Number(meta.recent_error_count ?? 0),
    status: meta.status || "Learning",
  };
}

function graphMetaRows(node) {
  const meta = node.meta || {};
  const rows = [];
  if (meta.stage) rows.push(["认知阶段", `Stage ${meta.stage}`]);
  if (meta.concept_id) rows.push(["考点编号", meta.concept_id]);
  if (meta.profile) rows.push(["学情画像", meta.profile]);
  if (meta.note) rows.push(["说明", meta.note]);
  const mastery = graphMasteryForNode(node.id);
  if (mastery) {
    rows.push(["建构期掌握度", `${Math.round(mastery.mastery * 100)}%`]);
    rows.push(["近期错误次数", String(mastery.errors)]);
    rows.push(["学情状态", mastery.status]);
  }
  if (!rows.length) return "";
  return `<div class="graph-meta-grid">
    ${rows.map(([key, value]) => `<span>${escapeHtml(key)}</span><b>${escapeHtml(value)}</b>`).join("")}
  </div>`;
}

function visibleGraphNodeIds() {
  const nodes = state.graph.nodes || [];
  const matches = graphSearchMatches();
  const ids = !state.graphQuery && !state.graphKind
    ? new Set(nodes.slice(0, 220).map((node) => node.id))
    : new Set(matches.map((node) => node.id));
  (state.graph.edges || []).forEach((edge) => {
    if (ids.has(edge.source)) ids.add(edge.target);
    if (ids.has(edge.target)) ids.add(edge.source);
  });
  if (state.selectedGraphNodeId) {
    ids.add(state.selectedGraphNodeId);
    graphPrerequisiteEdges(state.selectedGraphNodeId).forEach((edge) => ids.add(edge.source));
  }
  return ids;
}

function renderGraphFilters() {
  const select = $("#graphKindFilter");
  if (!select) return;
  const current = select.value;
  const kinds = [...new Set((state.graph.nodes || []).map((node) => node.kind))].sort();
  select.innerHTML = '<option value="">全部类型</option>' + kinds.map((kind) => `<option value="${escapeHtml(kind)}">${escapeHtml(displayKind(kind))}</option>`).join("");
  select.value = kinds.includes(current) ? current : "";
  state.graphKind = select.value;
}

function renderGraphResults() {
  if (!$("#graphResultList") || !$("#graphSelected")) return;
  const matches = graphSearchMatches();
  const visibleIds = visibleGraphNodeIds();
  const selected = (state.graph.nodes || []).find((node) => node.id === state.selectedGraphNodeId);
  $("#graphResultList").innerHTML =
    matches.length === 0
      ? '<div class="empty">没有匹配节点</div>'
      : matches
          .slice(0, 24)
          .map(
            (node) => `<button class="graph-result ${node.id === state.selectedGraphNodeId ? "active" : ""}" data-node-id="${escapeHtml(node.id)}" type="button">
              <strong>${escapeHtml(node.label)}</strong>
              <span>${escapeHtml(displayKind(node.kind))} · ${escapeHtml(node.description || "暂无描述").slice(0, 56)}</span>
            </button>`,
          )
          .join("");
  $$(".graph-result").forEach((button) => {
    button.onclick = () => selectGraphNode(button.dataset.nodeId);
  });

  if (!selected || !visibleIds.has(selected.id)) {
    $("#graphSelected").innerHTML = '<div class="empty">点击画布节点或检索结果查看详情</div>';
  } else {
    const related = (state.graph.edges || [])
      .filter((edge) => edge.source === selected.id || edge.target === selected.id)
      .slice(0, 8);
    const prerequisites = graphPrerequisiteEdges(selected.id);
    $("#graphSelected").innerHTML = `<article class="graph-selected-card">
      <strong>${escapeHtml(selected.label)}</strong>
      <span>${escapeHtml(displayKind(selected.kind))}</span>
      <p>${escapeHtml(selected.description || "暂无描述")}</p>
      ${graphMetaRows(selected)}
      <h4>前置相关节点</h4>
      <div class="graph-relation-list prerequisite-list">
        ${
          prerequisites.length
            ? prerequisites
                .map((edge) => {
                  const otherId = graphEdgeOtherId(edge, selected.id);
                  const source = (state.graph.nodes || []).find((node) => node.id === otherId);
                  return `<button class="graph-relation graph-prerequisite" data-node-id="${escapeHtml(otherId)}" type="button">
                    ${escapeHtml(source?.label || otherId)} ← ${escapeHtml(displayRelation(edge.relation))}
                  </button>`;
                })
                .join("")
            : '<span class="empty">暂无明确前置节点</span>'
        }
      </div>
      <h4>相邻关系</h4>
      <div class="graph-relation-list">
        ${
          related.length
            ? related
                .map((edge) => {
                  const otherId = graphEdgeOtherId(edge, selected.id);
                  const other = (state.graph.nodes || []).find((node) => node.id === otherId);
                  return `<button class="graph-relation" data-node-id="${escapeHtml(otherId)}" type="button">
                    ${escapeHtml(displayRelation(edge.relation))} → ${escapeHtml(other?.label || otherId)}
                  </button>`;
                })
                .join("")
            : '<span class="empty">暂无相邻关系</span>'
        }
      </div>
    </article>`;
    $$(".graph-relation").forEach((button) => {
      button.onclick = () => selectGraphNode(button.dataset.nodeId);
    });
  }
  const status = $("#graphStatus");
  if (status) status.textContent = `当前显示 ${visibleIds.size} 个节点，检索命中 ${matches.length} 个节点。点击节点可查看相邻关系。`;
}

function selectGraphNode(nodeId) {
  if (!nodeId) return;
  state.selectedGraphNodeId = nodeId;
  renderGraphResults();
  drawGraph();
}

function renderGraphSummary() {
  const counts = (state.graph.nodes || []).reduce((acc, node) => {
    acc[node.kind] = (acc[node.kind] || 0) + 1;
    return acc;
  }, {});
  $("#graphSummary").innerHTML = Object.entries(counts)
    .map(
      ([kind, count]) => `<article>
        <strong>${escapeHtml(displayKind(kind))}</strong>
        <span>${count} nodes</span>
      </article>`,
    )
    .join("");
}

function renderLegend() {
  const kinds = [...new Set((state.graph.nodes || []).map((node) => node.kind))].slice(0, 12);
  $("#graphLegend").innerHTML = kinds
    .map((kind) => `<span><i style="background:${kindColors[kind] || "#fff"}"></i>${escapeHtml(displayKind(kind))}</span>`)
    .join("");
}

function hashNumber(text) {
  let hash = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash >>> 0);
}

function graphPosition(node, index, width, height) {
  const centerX = width / 2;
  const centerY = height / 2;
  const tiers = {
    system: 0,
    layer: 1,
    theory: 1,
    workflow: 2,
    strategy: 2,
    guardrail: 2,
    agent: 3,
    ct_skill: 4,
    python_concept: 4,
    micro_concept: 4,
    error_pattern: 4,
    student_profile: 5,
    student_state: 5,
    document: 5,
    chunk: 5,
  };
  const tier = tiers[node.kind] ?? 5;
  if (tier === 0) return { x: centerX, y: centerY };
  const seed = hashNumber(node.id);
  const angle = ((seed % 360) / 180) * Math.PI + index * 0.21;
  const radius = Math.min(width, height) * (0.07 + tier * 0.07);
  return { x: centerX + Math.cos(angle) * radius, y: centerY + Math.sin(angle) * radius };
}

function drawGraph() {
  const canvas = $("#graphCanvas");
  if (!canvas) return;
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  canvas.width = Math.max(360, Math.floor(rect.width * ratio));
  canvas.height = Math.max(300, Math.floor(rect.height * ratio));
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  ctx.clearRect(0, 0, width, height);

  const visibleIds = visibleGraphNodeIds();
  const matchedIds = new Set(graphSearchMatches().map((node) => node.id));
  const selectedId = state.selectedGraphNodeId;
  const prerequisiteEdges = graphPrerequisiteEdges(selectedId);
  const prerequisiteNodeIds = new Set(prerequisiteEdges.map((edge) => edge.source));
  const prerequisiteEdgeKeys = new Set(prerequisiteEdges.map((edge) => `${edge.source}|${edge.target}|${edge.relation}`));
  const nodes = (state.graph.nodes || []).filter((node) => visibleIds.has(node.id)).slice(0, 220);
  const nodeMap = new Map();
  const tick = performance.now() / 1000;
  nodes.forEach((node, index) => {
    const base = graphPosition(node, index, width, height);
    const seed = hashNumber(node.id);
    const drift = node.kind === "system" ? 0 : 5 + (seed % 7);
    const manual = state.graphManualPositions[node.id];
    nodeMap.set(node.id, {
      ...node,
      x: manual ? manual.x * width : base.x + Math.sin(tick * 0.7 + seed) * drift,
      y: manual ? manual.y * height : base.y + Math.cos(tick * 0.55 + seed) * drift,
    });
  });
  state.graphLayout = nodeMap;

  ctx.save();
  const bg = ctx.createRadialGradient(width * 0.45, height * 0.42, 20, width * 0.5, height * 0.5, Math.max(width, height) * 0.72);
  bg.addColorStop(0, "#173b62");
  bg.addColorStop(0.52, "#091d33");
  bg.addColorStop(1, "#04111f");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();

  ctx.lineWidth = 1.6;
  (state.graph.edges || []).forEach((edge) => {
    const source = nodeMap.get(edge.source);
    const target = nodeMap.get(edge.target);
    if (!source || !target) return;
    const isSelectedEdge = edge.source === selectedId || edge.target === selectedId;
    const isPrerequisiteEdge = prerequisiteEdgeKeys.has(`${edge.source}|${edge.target}|${edge.relation}`);
    const isMatchedEdge = matchedIds.has(edge.source) || matchedIds.has(edge.target);
    const midX = (source.x + target.x) / 2;
    const midY = (source.y + target.y) / 2;
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const curve = Math.min(42, Math.max(-42, (hashNumber(edge.relation + edge.source) % 84) - 42));
    const length = Math.hypot(dx, dy) || 1;
    const cx = midX - (dy / length) * curve;
    const cy = midY + (dx / length) * curve;
    const grad = ctx.createLinearGradient(source.x, source.y, target.x, target.y);
    grad.addColorStop(0, isPrerequisiteEdge ? "rgba(102, 217, 232, 0.9)" : isSelectedEdge ? "rgba(255, 225, 122, 0.82)" : isMatchedEdge ? "rgba(102, 217, 232, 0.62)" : "rgba(95, 183, 255, 0.24)");
    grad.addColorStop(0.5, isPrerequisiteEdge ? "rgba(255, 255, 255, 0.95)" : isSelectedEdge ? "rgba(255, 255, 255, 0.9)" : isMatchedEdge ? "rgba(155, 231, 197, 0.62)" : "rgba(120, 229, 211, 0.42)");
    grad.addColorStop(1, isPrerequisiteEdge ? "rgba(168, 165, 255, 0.82)" : isSelectedEdge ? "rgba(255, 143, 163, 0.72)" : "rgba(255, 255, 255, 0.18)");
    ctx.lineWidth = isPrerequisiteEdge ? 3.8 : isSelectedEdge ? 3.2 : isMatchedEdge ? 2.2 : 1.4;
    ctx.strokeStyle = grad;
    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    ctx.quadraticCurveTo(cx, cy, target.x, target.y);
    ctx.stroke();
    if (hashNumber(edge.source + edge.target) % 5 === 0) {
      ctx.fillStyle = "rgba(219, 241, 255, 0.56)";
      ctx.font = '10px "Courier New", monospace';
      ctx.fillText(edge.relation, cx + 4, cy - 4);
    }
  });

  nodeMap.forEach((node) => {
    const color = kindColors[node.kind] || "#ffffff";
    const size = node.kind === "system" ? 21 : node.kind === "layer" || node.kind === "theory" ? 16 : node.kind === "agent" ? 13 : 10;
    const isSelected = node.id === selectedId;
    const isPrerequisite = prerequisiteNodeIds.has(node.id);
    const isMatched = matchedIds.has(node.id);
    ctx.save();
    ctx.shadowColor = color;
    ctx.shadowBlur = isSelected ? 34 : isPrerequisite ? 28 : isMatched ? 24 : node.kind === "system" ? 26 : 16;
    ctx.beginPath();
    ctx.arc(node.x, node.y, isSelected ? size + 5 : isPrerequisite ? size + 4 : isMatched ? size + 3 : size, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.lineWidth = isSelected ? 4 : isPrerequisite ? 3.6 : isMatched ? 3.2 : 2.4;
    ctx.strokeStyle = isSelected ? "#ffe17a" : isPrerequisite ? "#66d9e8" : isMatched ? "#ffffff" : "rgba(255,255,255,0.9)";
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(node.x - size * 0.32, node.y - size * 0.36, Math.max(2, size * 0.26), 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255,255,255,0.72)";
    ctx.fill();
    ctx.restore();
  });

  ctx.font = '12px "Courier New", monospace';
  ctx.fillStyle = "rgba(236, 248, 255, 0.92)";
  [...nodeMap.values()]
    .filter((node, index) => index < 32 || matchedIds.has(node.id) || prerequisiteNodeIds.has(node.id) || node.id === selectedId)
    .forEach((node) => {
    const label = node.label.length > 12 ? `${node.label.slice(0, 12)}…` : node.label;
    ctx.fillStyle = node.id === selectedId ? "#ffe17a" : prerequisiteNodeIds.has(node.id) ? "#9be7ff" : matchedIds.has(node.id) ? "#ffffff" : "rgba(236, 248, 255, 0.92)";
    ctx.fillText(label, Math.round(node.x + 14), Math.round(node.y - 10));
  });
}

function startGraphAnimation() {
  if (state.graphAnimating) return;
  state.graphAnimating = true;
  const loop = () => {
    if (!state.graphAnimating || state.page !== "graph") return;
    drawGraph();
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}

function pushMessage(role, title, content, target = "#messages") {
  const article = document.createElement("article");
  article.className = `message ${role}-message`;
  article.innerHTML = `<strong>${escapeHtml(title)}</strong><p>${escapeHtml(content)}</p>`;
  $(target).appendChild(article);
  $(target).scrollTop = $(target).scrollHeight;
}

function renderTrace(result, target = "#layerTrace") {
  const container = $(target);
  if (!container) return;
  const l1 = result.diagnosis;
  const gate = result.gate;
  const cards = [
    `<article class="trace-card" data-layer="L1">
      <strong>L1 诊断</strong>
      <span>${escapeHtml(l1.mode)} · ${escapeHtml(l1.task_type)} · ${escapeHtml(l1.student_profile)}</span>
      <p>${escapeHtml(l1.target_concept || "")}</p>
      <p>${escapeHtml(l1.diagnostic_sentence)}</p>
      <p>${escapeHtml(l1.cognitive_state || "")}</p>
      <div class="pill-row">${(l1.route || []).map((item) => `<b class="pill">${escapeHtml(item)}</b>`).join("")}</div>
    </article>`,
    ...(result.turns || []).map(
      (turn) => `<article class="trace-card" data-layer="L2">
        <strong>${escapeHtml(turn.agent)}</strong>
        <span>${escapeHtml(turn.focus)}</span>
        <p>${escapeHtml(turn.output)}</p>
      </article>`,
    ),
    `<article class="trace-card" data-layer="L3">
      <strong>L3 呈现</strong>
      <span>${escapeHtml(result.presentation.mode)} · ${escapeHtml(result.presentation.style)}</span>
      <div class="pill-row">${(result.presentation.workflow_steps || []).map((item) => `<b class="pill">${escapeHtml(item)}</b>`).join("")}</div>
      <p>${escapeHtml(result.presentation.orchestration?.name || "")}</p>
    </article>`,
    `<article class="trace-card" data-layer="GATE">
      <strong>教学门控</strong>
      <span>${gate.passed ? "通过" : "已调整"} · ${escapeHtml(gate.action)}</span>
      <div class="pill-row">${Object.entries(gate.rubric || {})
        .map(([key, value]) => `<b class="pill">${escapeHtml(key)} ${value}</b>`)
        .join("")}</div>
    </article>`,
  ];
  container.innerHTML = cards.join("");
}

function renderEvidence(result, target = "#evidenceList") {
  const container = $(target);
  if (!container) return;
  const chunks = result.retrieval?.evidence_chunks || [];
  container.innerHTML =
    chunks.length === 0
            ? '<div class="empty">当前使用内置图谱相关知识</div>'
      : chunks
          .map(
            (chunk) => `<article class="evidence-card">
              <strong>${escapeHtml(chunk.title || chunk.filename)} 相关知识 #${Number(chunk.chunk_index) + 1}</strong>
              <span>相关度 ${chunk.score}</span>
              <p>${escapeHtml(chunk.text_preview)}</p>
            </article>`,
          )
          .join("");
}

async function handleChat(event) {
  event.preventDefault();
  const input = $("#messageInput");
  const message = input.value.trim();
  if (!message) return;
  pushMessage("user", "课堂问题", message);
  input.value = "";
  pushMessage("system", "运行中", "教学模式：L1 正在诊断，L2 正在按流程调度，L3 正在整理反馈。");
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        mode: "teaching",
        profile: state.agentSettings.defaultProfile || "intermediate",
        style: $("#style").value,
        workflow: $("#workflow").value,
      }),
    });
    document.querySelector("#messages .system-message:last-child")?.remove();
    pushMessage("agent", `CT-GraphMAS #${result.interaction_id}`, result.presentation.answer);
    renderTrace(result);
    renderEvidence(result);
    await hydrate();
  } catch (error) {
    pushMessage("system", "错误", error.message);
  }
}

async function handleDailyChat(event) {
  event.preventDefault();
  const input = $("#dailyMessageInput");
  const message = input.value.trim();
  if (!message) return;
  pushMessage("user", "日常问题", message, "#dailyMessages");
  input.value = "";
  pushMessage("system", "运行中", "日常通用模式：正在检索必要图谱相关知识并生成低干扰提示。", "#dailyMessages");
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        mode: "daily",
        profile: state.agentSettings.defaultProfile || "intermediate",
        style: $("#dailyStyle").value,
        workflow: "standard",
      }),
    });
    document.querySelector("#dailyMessages .system-message:last-child")?.remove();
    pushMessage("agent", `日常答疑 #${result.interaction_id}`, result.presentation.answer, "#dailyMessages");
    renderTrace(result, "#dailyTrace");
    renderEvidence(result, "#dailyEvidence");
    await hydrate();
    navigate("daily");
  } catch (error) {
    pushMessage("system", "错误", error.message, "#dailyMessages");
  }
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function handleUpload() {
  const file = $("#fileInput").files?.[0];
  if (!file) {
    $("#uploadStatus").textContent = "请选择一个语料文件";
    return;
  }
  $("#uploadStatus").textContent = "正在切分并生成 embedding…";
  try {
    const dataUrl = await fileToDataUrl(file);
    const result = await api("/api/upload", {
      method: "POST",
      body: JSON.stringify({ filename: file.name, data_base64: dataUrl }),
    });
    $("#uploadStatus").textContent = `${result.filename}: ${result.chunks} 条相关知识已入库`;
    await hydrate();
    navigate("corpus");
  } catch (error) {
    $("#uploadStatus").textContent = error.message;
  }
}

async function handleKnowledgeUpload() {
  const file = $("#kbFileInput").files?.[0];
  if (!file) {
    $("#kbUploadStatus").textContent = "请先选择一个要加入知识库的文件。";
    return;
  }
  $("#kbUploadStatus").textContent = "正在切分、embedding，并写入知识库图谱…";
  try {
    const dataUrl = await fileToDataUrl(file);
    const result = await api("/api/upload", {
      method: "POST",
      body: JSON.stringify({ filename: file.name, data_base64: dataUrl }),
    });
    $("#kbUploadStatus").textContent = `${result.filename}: 已生成 ${result.chunks} 条相关知识，并写入知识库图谱。`;
    state.kbSelectedId = `doc:${result.document_id}`;
    await hydrate();
    navigate("knowledge");
  } catch (error) {
    $("#kbUploadStatus").textContent = error.message;
  }
}

function insertSample() {
  $("#messageInput").value = `我想做一个“校园活动推荐”小程序，输入兴趣和时间，输出推荐活动。我现在不知道应该先写 if，还是先用列表保存活动。请按 C-O-D-E-R 帮我拆一下，不要直接给完整代码。`;
}

function insertDailySample() {
  $("#dailyMessageInput").value = "我只是日常问一下，Python 列表为什么会下标越界？";
}

function readAgentSettingsForm() {
  const defaultMode = $("#defaultMode").value;
  return {
    defaultProfile: $("#defaultProfile").value,
    defaultMode,
    assignmentPolicy: $("#assignmentPolicy").value,
    defaultWorkflow: defaultMode === "daily" ? "standard" : $("#defaultWorkflow").value,
    defaultStyle: $("#defaultStyle").value,
    evidencePolicy: $("#evidencePolicy").value,
    agentP1: $("#agentP1").checked,
    agentP2: $("#agentP2").checked,
    agentP3: $("#agentP3").checked,
    agentP4: $("#agentP4").checked,
    antiGhostwrite: $("#antiGhostwrite").checked,
  };
}

function handleAgentSettingsSave(event) {
  event.preventDefault();
  state.agentSettings = { ...DEFAULT_AGENT_SETTINGS, ...readAgentSettingsForm() };
  localStorage.setItem("ctg_agent_settings", JSON.stringify(state.agentSettings));
  renderAgentSettings();
  $("#agentSettingsStatus").textContent = "多智能体配置已保存，并已同步到日常答疑与教学伴学页面。";
}

function guideVisualTemplate(content) {
  const screens = content.screens || [];
  return `<div class="guide-shot-stack">
    ${screens
      .map(
        (screen, index) => `<article class="guide-shot-card">
          <div class="guide-shot-frame">
            <img src="${escapeHtml(screen.src)}" alt="${escapeHtml(screen.title)}截图" />
          </div>
          <div>
            <b>${index + 1}. ${escapeHtml(screen.title)}</b>
            <p>${escapeHtml(screen.caption)}</p>
          </div>
        </article>`,
      )
      .join("")}
  </div>`;
}

function guideExampleTemplate(example) {
  if (!example) return "";
  return `<h3>${escapeHtml(example.title)}</h3>
    <div class="guide-question"><b>你可以这样输入</b><p>${escapeHtml(example.question)}</p></div>
    <div class="guide-answer"><b>系统会这样回应</b>
      ${(example.answer || []).map((line) => `<p>${escapeHtml(line)}</p>`).join("")}
    </div>`;
}

function guideApiTemplate(apiInfo) {
  if (!apiInfo) return "";
  return `<h3>${escapeHtml(apiInfo.title)}</h3><p>${escapeHtml(apiInfo.body)}</p>`;
}

function openGuide(type) {
  const content = guideContent[type] || guideContent.student;
  $("#guideEyebrow").textContent = content.eyebrow;
  $("#guideTitle").textContent = content.title;
  $("#guideBody").textContent = content.body;
  $("#guideSteps").innerHTML = content.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  $("#guideVisual").innerHTML = guideVisualTemplate(content);
  $("#guideExample").innerHTML = guideExampleTemplate(content.example);
  $("#guideApiWindow").innerHTML = guideApiTemplate(content.api);
  $("#guideModal").classList.remove("hidden");
}

function closeGuide() {
  $("#guideModal").classList.add("hidden");
}

function graphCanvasPoint(event) {
  const canvas = $("#graphCanvas");
  if (!canvas) return null;
  const rect = canvas.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
    width: rect.width,
    height: rect.height,
  };
}

function nearestGraphNodeAt(point) {
  if (!point || !state.graphLayout?.size) return null;
  let nearest = null;
  let nearestDistance = Infinity;
  state.graphLayout.forEach((node) => {
    const distance = Math.hypot(node.x - point.x, node.y - point.y);
    if (distance < nearestDistance) {
      nearest = node;
      nearestDistance = distance;
    }
  });
  return nearest && nearestDistance <= 32 ? { node: nearest, distance: nearestDistance } : null;
}

function handleGraphPointerDown(event) {
  const point = graphCanvasPoint(event);
  const hit = nearestGraphNodeAt(point);
  if (!hit) return;
  event.preventDefault();
  $("#graphCanvas").setPointerCapture?.(event.pointerId);
  state.graphDrag = {
    nodeId: hit.node.id,
    offsetX: point.x - hit.node.x,
    offsetY: point.y - hit.node.y,
    pointerId: event.pointerId,
    moved: false,
  };
  selectGraphNode(hit.node.id);
  $("#graphStatus").textContent = "拖动节点可以手动调整图谱位置，松开后会固定在当前位置。";
}

function handleGraphPointerMove(event) {
  if (!state.graphDrag) return;
  const point = graphCanvasPoint(event);
  if (!point) return;
  event.preventDefault();
  const x = Math.min(Math.max(point.x - state.graphDrag.offsetX, 24), point.width - 24);
  const y = Math.min(Math.max(point.y - state.graphDrag.offsetY, 24), point.height - 24);
  state.graphManualPositions[state.graphDrag.nodeId] = {
    x: x / point.width,
    y: y / point.height,
  };
  state.graphDrag.moved = true;
  drawGraph();
}

function handleGraphPointerUp(event) {
  if (!state.graphDrag) return;
  $("#graphCanvas").releasePointerCapture?.(event.pointerId);
  const nodeId = state.graphDrag.nodeId;
  state.graphDrag = null;
  selectGraphNode(nodeId);
  $("#graphStatus").textContent = "节点位置已固定。你可以继续搜索、点击或拖动其它节点。";
}

function resetGraphManualPositions() {
  state.graphManualPositions = {};
  state.graphDrag = null;
  $("#graphStatus").textContent = "已恢复自动布局。可搜索节点，也可以拖动节点重新排列。";
  drawGraph();
}

function handleGraphCanvasClick(event) {
  const hit = nearestGraphNodeAt(graphCanvasPoint(event));
  if (hit) {
    selectGraphNode(hit.node.id);
  }
}

async function handleAssignmentSubmit(event) {
  event.preventDefault();
  $("#assignmentStatus").textContent = "正在把任务写入班级任务池…";
  const payload = {
    class_name: $("#assignmentClass").value.trim(),
    target_profile: $("#assignmentProfile").value,
    workflow: $("#assignmentWorkflow").value,
    status: $("#assignmentStatusSelect").value,
    due_label: $("#assignmentDue").value.trim(),
    title: $("#assignmentTitle").value.trim(),
    description: $("#assignmentDescription").value.trim(),
  };
  try {
    const data = await api("/api/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.dashboard.tasks = data.tasks || [data.task, ...(state.dashboard.tasks || [])].filter(Boolean);
    if (data.tasks && state.dashboard.stats) state.dashboard.stats.tasks = data.tasks.length;
    renderStats();
    renderTasks();
    const visibleText = payload.status === "已分配" ? "学生端现在可以在“我的班级任务”里看到它。" : "任务已保存，发布前不会出现在学生端。";
    $("#assignmentStatus").textContent = `已保存《${payload.title}》。${visibleText}`;
  } catch (error) {
    $("#assignmentStatus").textContent = error.message;
  }
}

async function handleSettingsSave(event) {
  event.preventDefault();
  $("#settingsStatus").textContent = "正在保存 API 设置…";
  try {
    const data = await api("/api/settings", {
      method: "POST",
      body: JSON.stringify({
        provider: $("#apiProvider").value,
        base_url: $("#apiBaseUrl").value.trim(),
        api_key: $("#apiKey").value.trim(),
        chat_model: $("#chatModel").value.trim(),
        embedding_model: $("#embeddingModel").value.trim(),
        temperature: Number($("#temperature").value || 0.3),
        enabled: $("#apiEnabled").checked,
      }),
    });
    state.settings = data.settings || {};
    renderSettings();
    $("#settingsStatus").textContent = `已保存。当前提供方：${state.settings.provider || "local-demo"}`;
  } catch (error) {
    $("#settingsStatus").textContent = error.message;
  }
}

function bindEvents() {
  $("#loginForm").addEventListener("submit", handleLogin);
  $("#logoutBtn").addEventListener("click", logout);
  $("#dailyChatForm").addEventListener("submit", handleDailyChat);
  $("#chatForm").addEventListener("submit", handleChat);
  $("#uploadBtn").addEventListener("click", handleUpload);
  $("#kbUploadBtn").addEventListener("click", handleKnowledgeUpload);
  $("#dailySampleBtn").addEventListener("click", insertDailySample);
  $("#sampleBtn").addEventListener("click", insertSample);
  $("#agentSettingsForm").addEventListener("submit", handleAgentSettingsSave);
  $("#assignmentForm").addEventListener("submit", handleAssignmentSubmit);
  $("#settingsForm").addEventListener("submit", handleSettingsSave);
  $$(".guide-btn").forEach((button) => button.addEventListener("click", () => openGuide(button.dataset.guide)));
  $("#guideCloseBtn").addEventListener("click", closeGuide);
  $("#guideModal").addEventListener("click", (event) => {
    if (event.target.id === "guideModal") closeGuide();
  });
  $("#refreshGraphBtn").addEventListener("click", async () => {
    state.graph = await api("/api/graph");
    renderGraphSummary();
    renderGraphFilters();
    renderGraphResults();
    drawGraph();
    renderLegend();
  });
  $("#graphSearchInput").addEventListener("input", (event) => {
    state.graphQuery = event.target.value;
    renderGraphResults();
    drawGraph();
  });
  $("#graphKindFilter").addEventListener("change", (event) => {
    state.graphKind = event.target.value;
    renderGraphResults();
    drawGraph();
  });
  $("#clearGraphSearchBtn").addEventListener("click", () => {
    state.graphQuery = "";
    state.graphKind = "";
    state.selectedGraphNodeId = "";
    $("#graphSearchInput").value = "";
    $("#graphKindFilter").value = "";
    renderGraphResults();
    drawGraph();
  });
  $("#resetGraphLayoutBtn").addEventListener("click", resetGraphManualPositions);
  $("#graphCanvas").addEventListener("pointerdown", handleGraphPointerDown);
  $("#graphCanvas").addEventListener("pointermove", handleGraphPointerMove);
  $("#graphCanvas").addEventListener("pointerup", handleGraphPointerUp);
  $("#graphCanvas").addEventListener("pointercancel", handleGraphPointerUp);
  $("#graphCanvas").addEventListener("click", handleGraphCanvasClick);
  $("#kbRefreshBtn").addEventListener("click", async () => {
    state.corpus = await api("/api/corpus");
    state.graph = await api("/api/graph");
    renderKnowledgeBase();
  });
  $("#kbSearchInput").addEventListener("input", (event) => {
    state.kbQuery = event.target.value;
    renderKnowledgeBase();
  });
  $("#kbClearBtn").addEventListener("click", () => {
    state.kbQuery = "";
    state.kbSelectedId = "";
    $("#kbSearchInput").value = "";
    renderKnowledgeBase();
  });
  $("#kbGraphCanvas").addEventListener("click", handleKnowledgeCanvasClick);
  $("#defaultMode").addEventListener("change", () => {
    syncWorkflowAvailability();
  });
  $("#assignmentPolicy").addEventListener("change", syncAgentAllocationFields);
  $("#workflow").addEventListener("change", renderModeInfo);
  window.addEventListener("resize", () => {
    drawGraph();
    drawKnowledgeGraph();
  });
}

bindEvents();
checkSession();
