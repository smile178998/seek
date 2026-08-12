const STATUS_LABEL = {
  registered: "已注册",
  not_registered: "未注册",
  info: "情报",
  unknown: "无法判定",
  rate_limited: "被限流",
  error: "失败",
  skipped: "跳过",
};

const CATEGORY_LABEL = {
  social: "社交",
  shop: "电商",
  dev: "开发",
  profile: "资料",
  breach: "泄露库",
  domain: "域名",
  mail: "邮箱",
  music: "音乐",
  media: "媒体",
  forum: "论坛",
  crm: "CRM",
  payment: "支付",
  crowdfunding: "众筹",
  adult: "成人",
  osint: "情报源",
  edu: "教育",
  jobs: "招聘",
  medical: "医疗",
  sport: "运动",
  transport: "出行",
  realestate: "房产",
  other: "其他",
};

const DATA_LABEL = {
  username: "用户名",
  display_name: "昵称",
  profile_url: "主页",
  location: "位置",
  accounts: "关联账号",
  urls: "关联链接",
  breaches: "泄露事件",
  breach_dates: "泄露日期",
  mx: "MX 记录",
  providers: "服务商",
  disposable: "一次性邮箱",
  masked_phone: "手机号掩码",
  masked_email: "邮箱掩码",
};

const el = (id) => document.getElementById(id);
const state = {
  results: [],
  categories: [],
  activeCategories: new Set(),
  activeStatuses: new Set(),
  keyword: "",
  source: null,
  email: "",
  total: 0,
  mode: "scan", // scan | ai
  aiConfigured: false,
};

/* ---------------- 初始化 ---------------- */
async function init() {
  el("run").addEventListener("click", start);
  el("stop").addEventListener("click", stop);
  el("email").addEventListener("keydown", (e) => {
    if (e.key === "Enter") start();
  });
  el("keyword").addEventListener("input", (e) => {
    state.keyword = e.target.value.trim().toLowerCase();
    render();
  });
  el("export-json").addEventListener("click", exportJson);
  el("export-csv").addEventListener("click", exportCsv);
  document.querySelectorAll(".mode-chip").forEach((chip) => {
    chip.addEventListener("click", () => setMode(chip.dataset.mode));
  });

  initPwnedPassword();

  try {
    const [meta, providers] = await Promise.all([
      fetch("/api/meta").then((r) => r.json()),
      fetch("/api/providers").then((r) => r.json()),
    ]);
    applyMeta(meta, providers);
  } catch (err) {
    toast("无法连接后端服务：" + err.message, true);
  }
}

/* ---------------- 密码泄露检测（HIBP Pwned Passwords，纯前端 k-匿名） ---------------- */
function initPwnedPassword() {
  const input = el("pwned-input");
  const btn = el("pwned-check");
  const result = el("pwned-result");
  if (!input || !btn || !result) return;

  async function sha1Hex(text) {
    const bytes = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest("SHA-1", bytes);
    return Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
      .toUpperCase();
  }

  async function run() {
    const password = input.value;
    if (!password) {
      toast("请输入要检测的密码", true);
      return;
    }
    if (!window.isSecureContext || !window.crypto || !window.crypto.subtle) {
      toast("当前环境不支持 Web Crypto（需通过 HTTPS 或 localhost 访问）", true);
      return;
    }

    btn.disabled = true;
    const oldLabel = btn.textContent;
    btn.textContent = "检测中…";
    result.hidden = true;

    try {
      const hashHex = await sha1Hex(password);
      const prefix = hashHex.slice(0, 5);
      const suffix = hashHex.slice(5);

      // 只把哈希前 5 位发给 HIBP 官方接口（k-匿名协议），密码/完整哈希永不出浏览器
      const resp = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, {
        headers: { "Add-Padding": "true" },
      });
      if (!resp.ok) throw new Error(`HIBP 接口返回 HTTP ${resp.status}`);
      const text = await resp.text();

      let count = 0;
      for (const line of text.split("\n")) {
        const idx = line.indexOf(":");
        if (idx === -1) continue;
        if (line.slice(0, idx).trim() === suffix) {
          count = parseInt(line.slice(idx + 1), 10) || 0;
          break;
        }
      }

      result.hidden = false;
      if (count > 0) {
        result.className = "pwned-result bad";
        result.innerHTML = `⚠️ 该密码已在已知数据泄露库中出现过 <strong>${count.toLocaleString(
          "zh-CN"
        )}</strong> 次，属于<strong>高风险密码</strong>，请立即更换，并检查是否在其他站点重复使用。`;
      } else {
        result.className = "pwned-result ok";
        result.innerHTML = `✅ 未在 HIBP 已知泄露库（截至最近一次更新）中查到该密码的哈希。不代表绝对安全，仍建议使用密码管理器生成的唯一强密码。`;
      }
    } catch (err) {
      result.hidden = false;
      result.className = "pwned-result bad";
      result.textContent = "检测失败：" + err.message + "（可能是网络无法访问 api.pwnedpasswords.com）";
    } finally {
      btn.disabled = false;
      btn.textContent = oldLabel;
      input.value = "";
    }
  }

  btn.addEventListener("click", run);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") run();
  });
}

function setMode(mode) {
  if (mode === "ai" && !state.aiConfigured) {
    toast("请先在 .env 配置 SEEK_AI_API_KEY 并重启服务", true);
    return;
  }
  state.mode = mode;
  document.querySelectorAll(".mode-chip").forEach((c) => {
    c.classList.toggle("on", c.dataset.mode === mode);
  });
  el("filters-row").hidden = mode === "ai";
  el("run").querySelector(".btn-label").textContent =
    mode === "ai" ? "开始 AI 汇总" : "开始查询";
}

function applyMeta(meta, providers) {
  const ready = providers.filter((p) => p.ready).length;
  el("meta-providers").textContent = `${ready}/${providers.length} 个模块就绪`;

  const quotaParts = [];
  if (meta.rate_limit.scans > 0) {
    quotaParts.push(`剩余额度 ${meta.rate_limit.remaining}/${meta.rate_limit.scans}`);
  }
  if (meta.allowed_domains.length) {
    quotaParts.push(`仅限域名 ${meta.allowed_domains.join(" / ")}`);
  }
  el("meta-quota").textContent = quotaParts.join(" · ");
  el("meta-quota").hidden = quotaParts.length === 0;

  state.aiConfigured = !!(meta.ai && meta.ai.configured);
  const aiBtn = el("mode-ai");
  const aiHint = el("ai-status");
  const profile = meta.scan_profile || "reliable";
  const aiProfile = (meta.ai && meta.ai.profile) || meta.ai_profile || "reliable";
  el("meta-providers").textContent =
    `${ready}/${providers.length} 个模块就绪 · ${profile === "full" ? "完整" : "可靠"}模式`;
  if (state.aiConfigured) {
    aiBtn.disabled = false;
    aiHint.textContent = `AI 已就绪 · ${meta.ai.model || ""} · ${aiProfile === "full" ? "完整" : "可靠"}档`;
  } else {
    aiBtn.disabled = true;
    aiHint.textContent = "配置 SEEK_AI_API_KEY 后可用 · 默认可靠模式";
  }

  if (!meta.require_consent) el("consent-wrap").hidden = true;

  state.categories = meta.categories;
  const wrap = el("category-chips");
  wrap.innerHTML = "";
  meta.categories.forEach((cat) => {
    const count = providers.filter((p) => p.category === cat).length;
    const chip = document.createElement("button");
    chip.className = "chip on";
    chip.dataset.category = cat;
    chip.textContent = `${CATEGORY_LABEL[cat] || cat} (${count})`;
    chip.title = providers
      .filter((p) => p.category === cat)
      .map((p) => `${p.title}${p.ready ? "" : " · " + (p.unready_reason || "未就绪")}`)
      .join("\n");
    chip.addEventListener("click", () => {
      chip.classList.toggle("on");
      syncCategories();
    });
    wrap.appendChild(chip);
  });
  syncCategories();
}

function syncCategories() {
  state.activeCategories = new Set(
    [...document.querySelectorAll("#category-chips .chip.on")].map((c) => c.dataset.category)
  );
}

/* ---------------- 扫描 ---------------- */
function start() {
  if (state.source) return;

  const email = el("email").value.trim();
  if (!email) {
    toast("请输入要查询的邮箱", true);
    el("email").focus();
    return;
  }
  const consentWrap = el("consent-wrap");
  if (!consentWrap.hidden && !el("consent").checked) {
    consentWrap.classList.remove("shake");
    void consentWrap.offsetWidth;
    consentWrap.classList.add("shake");
    toast("请先勾选授权声明", true);
    return;
  }
  if (state.mode === "scan" && state.activeCategories.size === 0) {
    toast("请至少选择一个检测分类", true);
    return;
  }

  state.results = [];
  state.email = email;
  state.activeStatuses = new Set();
  state.keyword = "";
  el("keyword").value = "";

  el("results").innerHTML = "";
  el("results-panel").hidden = true;
  el("stats").hidden = true;
  el("ai-report-panel").hidden = true;
  el("progress-panel").hidden = false;
  el("progress-bar").style.width = "0%";
  el("progress-text").textContent = "正在建立连接…";
  el("progress-count").textContent = "0 / 0";
  setRunning(true);

  if (state.mode === "ai") {
    startAi(email);
    return;
  }

  const params = new URLSearchParams({
    email,
    consent: "true",
    only: [...state.activeCategories].join(","),
  });
  const source = new EventSource(`/api/scan/stream?${params.toString()}`);
  state.source = source;

  source.addEventListener("start", (e) => {
    const data = JSON.parse(e.data);
    state.total = data.total;
    el("progress-text").textContent = `正在检测 ${data.email}`;
    el("progress-count").textContent = `0 / ${data.total}`;
  });

  source.addEventListener("result", (e) => {
    const result = JSON.parse(e.data);
    state.results.push(result);
    const done = state.results.length;
    const pct = state.total ? Math.round((done / state.total) * 100) : 0;
    el("progress-bar").style.width = `${pct}%`;
    el("progress-count").textContent = `${done} / ${state.total}`;
    el("results-panel").hidden = false;
    render();
    renderStats();
  });

  source.addEventListener("summary", (e) => {
    const summary = JSON.parse(e.data);
    el("progress-text").textContent = `检测完成 · 耗时 ${(summary.elapsed_ms / 1000).toFixed(1)} 秒`;
    el("progress-bar").style.width = "100%";
    stop();
    renderStats(summary);
  });

  source.addEventListener("error", (e) => {
    if (e.data) {
      try {
        toast(JSON.parse(e.data).message, true);
      } catch {
        toast("服务端返回了错误", true);
      }
    } else if (!state.results.length) {
      toast("连接中断，请检查邮箱格式、授权勾选或访问频率限制", true);
      el("progress-text").textContent = "已中断";
    }
    stop();
  });
}

function startAi(email) {
  const params = new URLSearchParams({ email, consent: "true" });
  const source = new EventSource(`/api/ai/investigate?${params.toString()}`);
  state.source = source;
  const logBox = el("ai-log");
  logBox.hidden = false;
  logBox.textContent = "";
  el("ai-report-panel").hidden = false;

  const appendLog = (line) => {
    logBox.textContent += line + "\n";
    logBox.scrollTop = logBox.scrollHeight;
  };

  source.addEventListener("ai_start", (e) => {
    const d = JSON.parse(e.data);
    const profileLabel = d.profile === "full" ? "完整" : "可靠";
    el("progress-text").textContent = `${profileLabel}检测聚合中 · ${d.model}`;
    el("progress-count").textContent = "…";
    appendLog(`模型 ${d.model} @ ${d.base_url}`);
    appendLog(`档位：${profileLabel}（SEEK_AI_PROFILE=${d.profile || "reliable"}）`);
  });

  source.addEventListener("aggregate_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = "正在运行可靠检测工具…";
    appendLog(`启动后端: ${(d.backends || []).join(", ")}`);
  });

  source.addEventListener("backend_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `工具运行中 · ${d.name}`;
    appendLog(`▶ ${d.name} (${d.modules || "?"} 模块)`);
  });

  source.addEventListener("backend_done", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`✓ ${d.name} 完成 ${JSON.stringify(d).slice(0, 120)}`);
  });

  source.addEventListener("backend_skip", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`○ 跳过 ${d.name}: ${d.reason || ""}`);
  });

  source.addEventListener("aggregate_done", (e) => {
    const d = JSON.parse(e.data);
    const s = d.stats || {};
    el("progress-bar").style.width = "55%";
    el("progress-text").textContent =
      `聚合完成 · 有效判定 ${s.effective ?? "?"} · 已注册 ${s.registered ?? d.merged_registered_count ?? 0}`;
    appendLog(
      `聚合完成：有效 ${s.effective ?? "?"} / 已注册 ${s.registered ?? 0} / 未注册 ${s.not_registered ?? 0} / 情报 ${s.intel ?? 0}`
    );
  });

  source.addEventListener("ai_thinking", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `AI 汇总中 · 第 ${d.round}/${d.max} 轮`;
    el("progress-bar").style.width = `${Math.min(95, 55 + d.round * 8)}%`;
    appendLog(`AI 汇总轮次 ${d.round}`);
  });

  source.addEventListener("ai_tool", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`调用工具 ${d.name}`);
    el("progress-text").textContent = `AI 调用工具 · ${d.name}`;
  });

  source.addEventListener("ai_tool_result", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`← ${d.name}: ${(d.preview || "").slice(0, 80)}`);
  });

  source.addEventListener("result", (e) => {
    const result = JSON.parse(e.data);
    state.results.push(result);
    el("results-panel").hidden = false;
    render();
    renderStats();
  });

  source.addEventListener("ai_report", (e) => {
    const report = JSON.parse(e.data);
    renderAiReport(report);
    el("progress-text").textContent = "AI 探查完成";
    el("progress-bar").style.width = "100%";
    stop();
  });

  source.addEventListener("error", (e) => {
    if (e.data) {
      try {
        toast(JSON.parse(e.data).message, true);
      } catch {
        toast("AI 探查出错", true);
      }
    } else if (!state.results.length) {
      toast("AI 连接中断，请确认已配置 API Key 并重启服务", true);
    }
    el("progress-text").textContent = "已中断";
    stop();
  });
}

function renderAiReport(report) {
  el("ai-report-panel").hidden = false;
  el("ai-summary").textContent = report.summary || "";

  const stats = report.stats || {};
  const statsBox = el("ai-stats");
  const cells = [
    ["effective", "有效判定", "ok"],
    ["registered", "已注册", ""],
    ["not_registered", "未注册", ""],
    ["intel", "情报", ""],
    ["failed", "失败/未知", "warn"],
  ];
  if (stats && (stats.effective != null || stats.checked != null)) {
    statsBox.hidden = false;
    statsBox.innerHTML = cells
      .map(([key, label, cls]) => {
        const n = stats[key] ?? 0;
        return `<div class="ai-stat ${cls}"><strong>${n}</strong><span>${label}</span></div>`;
      })
      .join("");
  } else {
    statsBox.hidden = true;
    statsBox.innerHTML = "";
  }

  const fill = (id, items) => {
    const box = el(id);
    box.innerHTML = "";
    (items || []).forEach((item) => {
      const li = document.createElement("li");
      const title = item.site || item;
      li.innerHTML = `<strong>${escapeHtml(typeof title === "string" ? title : String(title))}</strong>`;
      if (item.evidence) {
        const s = document.createElement("small");
        s.textContent = item.evidence;
        li.appendChild(s);
      }
      if (item.url) {
        const a = document.createElement("a");
        a.href = item.url;
        a.target = "_blank";
        a.rel = "noreferrer";
        a.textContent = " 打开";
        a.style.color = "var(--accent)";
        li.appendChild(a);
      }
      box.appendChild(li);
    });
    if (!(items || []).length) {
      box.innerHTML = "<li><small>暂无</small></li>";
    }
  };
  fill("ai-confirmed", report.confirmed);
  fill("ai-intel", report.intel);
  fill("ai-not-registered", report.not_registered);
  fill("ai-likely", report.likely);
  const next = el("ai-next");
  if (report.next_steps && report.next_steps.length) {
    next.innerHTML =
      "<strong>建议下一步</strong><ol>" +
      report.next_steps.map((s) => `<li>${escapeHtml(s)}</li>`).join("") +
      "</ol>";
  } else {
    next.innerHTML = "";
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function stop() {
  if (state.source) {
    state.source.close();
    state.source = null;
  }
  setRunning(false);
}

function setRunning(running) {
  el("run").disabled = running;
  const idle = state.mode === "ai" ? "开始 AI 汇总" : "开始查询";
  el("run").querySelector(".btn-label").textContent = running ? "检测中…" : idle;
  el("stop").hidden = !running;
}

/* ---------------- 渲染 ---------------- */
const STATUS_ORDER = ["registered", "info", "unknown", "rate_limited", "not_registered", "error", "skipped"];

function render() {
  renderStatusFilters();
  const box = el("results");
  const rows = state.results
    .filter((r) => !state.activeStatuses.size || state.activeStatuses.has(r.status))
    .filter((r) => !state.keyword || `${r.title} ${r.provider}`.toLowerCase().includes(state.keyword))
    .sort(
      (a, b) =>
        STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status) ||
        a.title.localeCompare(b.title, "zh")
    );

  box.innerHTML = "";
  rows.forEach((r) => box.appendChild(rowNode(r)));
  el("empty").hidden = rows.length > 0;
}

function rowNode(r) {
  const row = document.createElement("div");
  row.className = "row";

  const badge = document.createElement("span");
  badge.className = `badge ${r.status}`;
  badge.textContent = STATUS_LABEL[r.status] || r.status;
  row.appendChild(badge);

  const main = document.createElement("div");
  main.className = "row-main";

  const title = document.createElement("div");
  title.className = "row-title";
  if (r.homepage) {
    const link = document.createElement("a");
    link.href = r.homepage;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    link.textContent = r.title;
    title.appendChild(link);
  } else {
    const name = document.createElement("span");
    name.className = "name";
    name.textContent = r.title;
    title.appendChild(name);
  }
  const tag = document.createElement("span");
  tag.className = "tag";
  tag.textContent = CATEGORY_LABEL[r.category] || r.category;
  title.appendChild(tag);
  main.appendChild(title);

  if (r.detail) {
    const detail = document.createElement("div");
    detail.className = "row-detail";
    detail.textContent = r.detail;
    main.appendChild(detail);
  }

  const entries = Object.entries(r.data || {});
  if (entries.length) {
    const data = document.createElement("div");
    data.className = "row-data";
    entries.forEach(([k, v]) => {
      const line = document.createElement("div");
      const key = document.createElement("span");
      key.className = "k";
      key.textContent = (DATA_LABEL[k] || k) + ":";
      const val = document.createElement("span");
      val.className = "v";
      val.textContent = Array.isArray(v) ? v.join(", ") : String(v);
      line.append(key, val);
      data.appendChild(line);
    });
    main.appendChild(data);
  }
  row.appendChild(main);

  const meta = document.createElement("div");
  meta.className = "row-meta";
  meta.textContent = [r.http_status ? `HTTP ${r.http_status}` : "", `${r.elapsed_ms}ms`]
    .filter(Boolean)
    .join(" · ");
  row.appendChild(meta);

  return row;
}

function renderStatusFilters() {
  const counts = {};
  state.results.forEach((r) => (counts[r.status] = (counts[r.status] || 0) + 1));
  const wrap = el("status-filters");
  wrap.innerHTML = "";
  STATUS_ORDER.filter((s) => counts[s]).forEach((status) => {
    const chip = document.createElement("button");
    chip.className = "chip" + (state.activeStatuses.has(status) ? " on" : "");
    chip.textContent = `${STATUS_LABEL[status]} ${counts[status]}`;
    chip.addEventListener("click", () => {
      state.activeStatuses.has(status)
        ? state.activeStatuses.delete(status)
        : state.activeStatuses.add(status);
      render();
    });
    wrap.appendChild(chip);
  });
}

function renderStats(summary) {
  const counts = summary || {};
  if (!summary) {
    STATUS_ORDER.forEach((s) => (counts[s] = state.results.filter((r) => r.status === s).length));
  }
  const tiles = [
    { key: "registered", label: "已注册", cls: "is-registered" },
    { key: "info", label: "情报", cls: "is-info" },
    { key: "unknown", label: "无法判定", cls: "is-unknown" },
    { key: "not_registered", label: "未注册", cls: "" },
    { key: "error", label: "失败/限流", cls: "is-error", extra: "rate_limited" },
  ];
  const box = el("stats");
  box.innerHTML = "";
  tiles.forEach((t) => {
    const value = (counts[t.key] || 0) + (t.extra ? counts[t.extra] || 0 : 0);
    const node = document.createElement("div");
    node.className = `stat ${t.cls}`;
    node.innerHTML = `<div class="stat-value">${value}</div><div class="stat-label">${t.label}</div>`;
    box.appendChild(node);
  });
  box.hidden = false;
}

/* ---------------- 导出 ---------------- */
function download(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function slug() {
  return state.email.replace(/[^a-z0-9]/gi, "_");
}

function exportJson() {
  if (!state.results.length) return toast("暂无结果可导出", true);
  download(
    `seek_${slug()}.json`,
    JSON.stringify({ email: state.email, generated_at: new Date().toISOString(), results: state.results }, null, 2),
    "application/json"
  );
}

function exportCsv() {
  if (!state.results.length) return toast("暂无结果可导出", true);
  const header = ["站点", "标识", "分类", "状态", "说明", "HTTP", "耗时(ms)", "附加数据"];
  const escape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = [header.map(escape).join(",")];
  state.results.forEach((r) => {
    lines.push(
      [
        r.title,
        r.provider,
        CATEGORY_LABEL[r.category] || r.category,
        STATUS_LABEL[r.status] || r.status,
        r.detail || "",
        r.http_status || "",
        r.elapsed_ms,
        JSON.stringify(r.data || {}),
      ]
        .map(escape)
        .join(",")
    );
  });
  download(`seek_${slug()}.csv`, "\uFEFF" + lines.join("\r\n"), "text/csv;charset=utf-8");
}

/* ---------------- 提示 ---------------- */
let toastTimer = null;
function toast(message, bad = false) {
  let node = document.querySelector(".toast");
  if (!node) {
    node = document.createElement("div");
    node.className = "toast";
    document.body.appendChild(node);
  }
  node.textContent = message;
  node.classList.toggle("bad", bad);
  requestAnimationFrame(() => node.classList.add("show"));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove("show"), 4200);
}

init();
