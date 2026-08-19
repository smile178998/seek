let STATUS_LABEL = {
  registered: "已注册",
  not_registered: "未注册",
  info: "情报",
  unknown: "无法判定",
  rate_limited: "被限流",
  error: "失败",
  skipped: "跳过",
};

let CATEGORY_LABEL = {
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

let DATA_LABEL = {
  username: "用户名",
  display_name: "昵称",
  profile_url: "主页",
  avatar_url: "头像",
  user_id: "用户 ID",
  name: "姓名",
  streak: "连续学习天数",
  has_plus: "付费会员",
  has_google_id: "已绑定 Google",
  has_facebook_id: "已绑定 Facebook",
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

const LABELS_ZH = {
  status: { ...STATUS_LABEL },
  category: { ...CATEGORY_LABEL },
  data: { ...DATA_LABEL },
};

const LABELS_EN = {
  status: {
    registered: "Registered",
    not_registered: "Not registered",
    info: "Intelligence",
    unknown: "Unknown",
    rate_limited: "Rate limited",
    error: "Failed",
    skipped: "Skipped",
  },
  category: {
    social: "Social", shop: "Shopping", dev: "Development", profile: "Profiles",
    breach: "Breaches", domain: "Domain", mail: "Email", music: "Music",
    media: "Media", forum: "Forums", crm: "CRM", payment: "Payments",
    crowdfunding: "Crowdfunding", adult: "Adult", osint: "Intelligence",
    edu: "Education", jobs: "Jobs", medical: "Health", sport: "Sports",
    transport: "Travel", realestate: "Real estate", other: "Other",
  },
  data: {
    username: "Username", display_name: "Display name", profile_url: "Profile",
    avatar_url: "Avatar", user_id: "User ID", name: "Name", streak: "Learning streak",
    has_plus: "Paid subscriber", has_google_id: "Google linked",
    has_facebook_id: "Facebook linked", location: "Location", accounts: "Linked accounts",
    urls: "Related links", breaches: "Breaches", breach_dates: "Breach dates",
    mx: "MX records", providers: "Providers", disposable: "Disposable email",
    masked_phone: "Masked phone", masked_email: "Masked email",
  },
};

const UI_TEXT = {
  zh: {
    pageTitle: "Seek · 邮箱注册痕迹反查", brandSubtitle: "邮箱注册痕迹反查",
    apiDocs: "API 文档", reliableScan: "可靠扫描", extendedScan: "扩展扫描",
    aiSummaryMode: "AI 可靠汇总", reliableHint: "可靠扫描：仅运行已验证站点，速度更快",
    extendedHint: "扩展扫描：覆盖更多候选站点，耗时和受限结果会增加",
    startQuery: "开始查询", startExtended: "开始扩展查询", startPhone: "查询手机号", startAi: "开始 AI 汇总",
    phoneScan: "手机号扫描", phoneHint: "手机号扫描：仅运行已配置 phone_request 的站点",
    emailPlaceholder: "somebody@example.com", phonePlaceholder: "+1 202 555 0123", enterPhone: "请输入手机号",
    stop: "停止", preparing: "准备中…", filterSites: "过滤站点…",
    exportJson: "导出 JSON", exportCsv: "导出 CSV", emptyResults: "没有符合当前筛选条件的结果",
    aiReport: "AI 汇总报告", confirmedRegistered: "已确认注册", domainIntel: "域名 / 邮箱情报",
    confirmedNotRegistered: "明确未注册", likelyClues: "疑似线索", noticeTitle: "使用须知",
    noticeAuthorized: "本工具仅用于<strong>本人账号资产梳理</strong>与<strong>已授权的安全评估</strong>。未经授权针对他人查询可能违反《个人信息保护法》《网络安全法》及目标站点服务条款。",
    noticeEvidence: "结果仅为探测推断：站点改版、风控拦截、CDN 缓存都可能造成误报或漏报，<strong>不可作为结论性证据</strong>。",
    noticeProfiles: "「可靠扫描」只运行经过验证的高可用模块；「扩展扫描」会加入更多候选规则，但更慢，也更容易受到站点风控影响。已注册为空通常表示未命中，不等于故障。",
    noticeOfficial: "内置模块只使用站点<strong>官方公开提供</strong>的查询接口。如需扩展，请在 <code>seek/definitions/</code> 下自行添加规则，并自行确认合法性。",
    switchLanguage: "Switch to English", languageButton: "English", running: "检测中…",
    noResultsExport: "暂无结果可导出", yes: "是", no: "否", open: "打开", none: "暂无",
    backendUnavailable: "无法连接后端服务：", startFailed: "启动查询失败：",
    configureAi: "请先在 .env 配置 SEEK_AI_API_KEY 并重启服务", enterEmail: "请输入要查询的邮箱",
    connecting: "正在建立连接…", reliableLabel: "可靠扫描", extendedLabel: "扩展扫描",
    scanning: "正在检测", scanComplete: "检测完成", elapsed: "耗时", seconds: "秒",
    serverError: "服务端返回了错误", connectionInterrupted: "请求中断，请检查后端服务、网络或访问频率限制",
    invalidPhone: "手机号格式无效，请使用国际格式", authFailure: "第三方服务认证失败",
    rateLimitFailure: "请求被限流，请稍后重试", timeoutFailure: "请求超时，请稍后重试",
    corsFailure: "跨域请求被浏览器阻止，请使用后端提供的网页地址", emptyScan: "没有可用的手机号扫描目标",
    interrupted: "已中断", aiReady: "AI 已就绪", reliableTier: "可靠档", extendedTier: "扩展档",
    aiAggregating: "检测聚合中", runningTools: "正在运行可靠检测工具…", toolRunning: "工具运行中",
    model: "模型", tier: "档位", startingBackends: "启动后端", modules: "模块", completed: "完成",
    skipped: "跳过", aggregateComplete: "聚合完成", effective: "有效判定", registered: "已注册",
    notRegistered: "未注册", intel: "情报", aiSummarizing: "AI 汇总中", round: "轮",
    callingTool: "AI 调用工具", aiComplete: "AI 探查完成", aiError: "AI 探查出错",
    aiDisconnected: "AI 连接中断，请确认已配置 API Key 并重启服务",
    failedUnknown: "失败/未知", nextSteps: "建议下一步", viewPublicAvatar: "查看公开头像",
  },
  en: {
    pageTitle: "Seek · Email Account Footprint Scanner", brandSubtitle: "Email account footprint scanner",
    apiDocs: "API Docs", reliableScan: "Reliable scan", extendedScan: "Extended scan",
    aiSummaryMode: "AI summary", reliableHint: "Reliable scan: verified sites only, with faster results",
    extendedHint: "Extended scan: more candidate sites, with longer runtimes and more blocked results",
    startQuery: "Start scan", startExtended: "Start extended scan", startPhone: "Scan phone number", startAi: "Start AI summary",
    phoneScan: "Phone scan", phoneHint: "Phone scan: only sites with phone_request are checked",
    emailPlaceholder: "somebody@example.com", phonePlaceholder: "+1 202 555 0123", enterPhone: "Enter a phone number",
    stop: "Stop", preparing: "Preparing…", filterSites: "Filter sites…",
    exportJson: "Export JSON", exportCsv: "Export CSV", emptyResults: "No results match the current filters",
    aiReport: "AI Summary Report", confirmedRegistered: "Confirmed registrations",
    domainIntel: "Domain / email intelligence", confirmedNotRegistered: "Confirmed not registered",
    likelyClues: "Potential clues", noticeTitle: "Important notice",
    noticeAuthorized: "Use this tool only for <strong>your own account inventory</strong> or an <strong>authorized security assessment</strong>. Unauthorized searches may violate privacy laws and target-site terms.",
    noticeEvidence: "Results are signals, not proof. Site changes, anti-abuse controls, and CDN caches can cause false positives or omissions. <strong>Do not treat them as conclusive evidence.</strong>",
    noticeProfiles: "Reliable scan runs verified high-availability modules. Extended scan adds more candidates, but is slower and more likely to encounter anti-abuse controls. No registered result usually means no match, not a system failure.",
    noticeOfficial: "Built-in modules use only <strong>official, publicly exposed</strong> site endpoints. Add custom rules under <code>seek/definitions/</code> only after confirming their legality.",
    switchLanguage: "切换为中文", languageButton: "中文", running: "Scanning…",
    noResultsExport: "There are no results to export", yes: "Yes", no: "No", open: "Open", none: "None",
    backendUnavailable: "Unable to connect to the backend: ", startFailed: "Failed to start scan: ",
    configureAi: "Configure SEEK_AI_API_KEY in .env and restart the service first",
    enterEmail: "Enter an email address to scan", connecting: "Connecting…",
    reliableLabel: "Reliable scan", extendedLabel: "Extended scan", scanning: "Scanning",
    scanComplete: "Scan complete", elapsed: "Elapsed", seconds: "seconds", serverError: "The server returned an error",
    connectionInterrupted: "Request interrupted. Check the backend, network, or rate limit",
    invalidPhone: "Invalid phone number format. Use international format", authFailure: "The third-party service rejected authentication",
    rateLimitFailure: "The request was rate limited. Try again later", timeoutFailure: "The request timed out. Try again later",
    corsFailure: "The browser blocked the cross-origin request. Use the backend web address", emptyScan: "No phone scan targets are available",
    interrupted: "Interrupted", aiReady: "AI ready", reliableTier: "Reliable tier", extendedTier: "Extended tier",
    aiAggregating: "Aggregating scan results", runningTools: "Running reliable detection tools…",
    toolRunning: "Tool running", model: "Model", tier: "Tier", startingBackends: "Starting backends",
    modules: "modules", completed: "completed", skipped: "Skipped", aggregateComplete: "Aggregation complete",
    effective: "Effective verdicts", registered: "Registered", notRegistered: "Not registered",
    intel: "Intelligence", aiSummarizing: "AI summarizing", round: "round", callingTool: "AI tool call",
    aiComplete: "AI investigation complete", aiError: "AI investigation failed",
    aiDisconnected: "AI connection interrupted. Confirm the API key is configured and restart the service",
    failedUnknown: "Failed / unknown", nextSteps: "Suggested next steps", viewPublicAvatar: "View public avatar",
  },
};

const SITE_TITLE_EN = {
  "博客园（CNBlogs）": "CNBlogs",
  "Gitee（码云）": "Gitee",
  "小众软件社区": "Appinn Community",
  "飞致云社区": "FIT2CLOUD Community",
  "openEuler 论坛": "openEuler Forum",
  "邮件服务商识别": "Email provider identification",
  "域名 MX 记录": "Domain MX records",
  "一次性邮箱识别": "Disposable email detection",
  "Gravatar 头像": "Gravatar avatar",
  "Gravatar 公开资料": "Gravatar public profile",
};

function localizeTitle(title) {
  return state.lang === "en" ? (SITE_TITLE_EN[title] || title) : title;
}

function localizeDetail(detail, status) {
  if (state.lang !== "en" || !detail || !/[\u3400-\u9fff]/.test(detail)) return detail;
  const generic = {
    registered: "The site reports that this email is registered.",
    not_registered: "The site reports that this email is currently available.",
    info: "Public email or domain intelligence was returned.",
    unknown: "The site did not return a conclusive account status.",
    rate_limited: "The request was blocked or rate limited by the site.",
    error: "The site request failed.",
    skipped: "This check was skipped.",
  };
  return generic[status] || "The site returned an unrecognized response.";
}

const el = (id) => document.getElementById(id);
const state = {
  results: [],
  activeStatuses: new Set(),
  keyword: "",
  source: null,
  email: "",
  total: 0,
  mode: "scan", // scan | ai
  scanProfile: "full", // reliable | full
  aiConfigured: false,
  aiMeta: null,
  lang: localStorage.getItem("seek-language") === "en" ? "en" : "zh",
};

function t(key) {
  return (UI_TEXT[state.lang] && UI_TEXT[state.lang][key]) || UI_TEXT.zh[key] || key;
}

function applyLanguage() {
  document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
  document.title = t("pageTitle");
  STATUS_LABEL = state.lang === "en" ? LABELS_EN.status : LABELS_ZH.status;
  CATEGORY_LABEL = state.lang === "en" ? LABELS_EN.category : LABELS_ZH.category;
  DATA_LABEL = state.lang === "en" ? LABELS_EN.data : LABELS_ZH.data;

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((node) => {
    node.innerHTML = t(node.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  const toggle = el("language-toggle");
  toggle.textContent = t("languageButton");
  toggle.setAttribute("aria-label", t("switchLanguage"));
  updateModeHint();
  updateInputMode();
  setRunning(!!state.source);
  render();
  if (state.results.length) renderStats();
}

function toggleLanguage() {
  state.lang = state.lang === "zh" ? "en" : "zh";
  localStorage.setItem("seek-language", state.lang);
  applyLanguage();
}

/* ---------------- 初始化 ---------------- */
async function init() {
  el("language-toggle").addEventListener("click", toggleLanguage);
  applyLanguage();
  el("run").addEventListener("click", safeStart);
  el("stop").addEventListener("click", stop);
  el("email").addEventListener("keydown", (e) => {
    if (e.key === "Enter") safeStart();
  });
  el("keyword").addEventListener("input", (e) => {
    state.keyword = e.target.value.trim().toLowerCase();
    render();
  });
  el("export-json").addEventListener("click", exportJson);
  el("export-csv").addEventListener("click", exportCsv);
  document.querySelectorAll(".mode-chip").forEach((chip) => {
    chip.addEventListener("click", () => setMode(chip.dataset.mode, chip.dataset.profile));
  });

  try {
    const meta = await fetch("/api/meta").then((r) => r.json());
    applyMeta(meta);
  } catch (err) {
    toast(t("backendUnavailable") + err.message, true);
  }
}

function safeStart() {
  try {
    start();
  } catch (err) {
    console.error("Failed to start scan", err);
    toast(t("startFailed") + (err.message || err), true);
    setRunning(false);
  }
}

function setMode(mode, profile = null) {
  if (mode === "ai" && !state.aiConfigured) {
    toast(t("configureAi"), true);
    return;
  }
  state.mode = mode;
  if (mode === "scan" && profile) state.scanProfile = profile;
  document.querySelectorAll(".mode-chip").forEach((c) => {
    const selected = c.dataset.mode === mode &&
      (mode === "ai" || mode === "phone" || c.dataset.profile === state.scanProfile);
    c.classList.toggle("on", selected);
  });
  el("run").querySelector(".btn-label").textContent =
    mode === "ai" ? t("startAi") : mode === "phone" ? t("startPhone") :
      state.scanProfile === "full" ? t("startExtended") : t("startQuery");
  updateInputMode();
  updateModeHint();
}

function updateInputMode() {
  const input = el("email");
  const phone = state.mode === "phone";
  input.type = phone ? "tel" : "email";
  input.placeholder = t(phone ? "phonePlaceholder" : "emailPlaceholder");
  input.setAttribute("aria-label", t(phone ? "phoneScan" : "emailPlaceholder"));
}

function applyMeta(meta) {
  state.aiConfigured = !!(meta.ai && meta.ai.configured);
  state.aiMeta = meta.ai || null;
  const aiBtn = el("mode-ai");
  const aiProfile = (meta.ai && meta.ai.profile) || meta.ai_profile || "reliable";
  if (state.aiConfigured) {
    aiBtn.disabled = false;
  } else {
    aiBtn.disabled = true;
  }
  state.aiMeta = { ...(meta.ai || {}), profile: aiProfile };
  updateModeHint();
}

function updateModeHint() {
  const hint = el("mode-status");
  if (state.mode === "phone") {
    hint.textContent = t("phoneHint");
    return;
  }
  if (state.mode === "ai") {
    const meta = state.aiMeta || {};
    hint.textContent = `${t("aiReady")} · ${meta.model || ""} · ${meta.profile === "full" ? t("extendedTier") : t("reliableTier")}`;
    return;
  }
  hint.textContent = state.scanProfile === "full"
    ? t("extendedHint")
    : t("reliableHint");
}

/* ---------------- 扫描 ---------------- */
function createPostEventStream(url, payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(new DOMException("Request timed out", "TimeoutError")), 90000);
  const listeners = new Map();
  let closed = false;
  const source = {
    addEventListener(name, listener) {
      const group = listeners.get(name) || [];
      group.push(listener);
      listeners.set(name, group);
    },
    close() {
      closed = true;
      clearTimeout(timeoutId);
      controller.abort();
    },
  };
  const dispatch = (name, data = "") => {
    for (const listener of listeners.get(name) || []) listener({ data });
  };

  queueMicrotask(async () => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(payload),
        credentials: "same-origin",
        cache: "no-store",
        referrerPolicy: "no-referrer",
        signal: controller.signal,
      });
      if (!response.ok || !response.body) {
        const body = await response.text();
        let detail = body;
        try {
          const parsed = JSON.parse(body);
          detail = Array.isArray(parsed.detail)
            ? parsed.detail.map((item) => item.msg || item).join("; ")
            : parsed.detail || parsed.message || body;
        } catch {
          // Keep the raw response when the server did not return JSON.
        }
        dispatch("error", JSON.stringify({
          code: response.status === 422 ? "invalid_phone" : response.status === 401 || response.status === 403 ? "auth_failure" : response.status === 429 ? "rate_limited" : "backend_error",
          status: response.status,
          message: detail || `HTTP ${response.status}`,
        }));
        return;
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (!closed) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const frames = buffer.split(/\r?\n\r?\n/);
        buffer = frames.pop() || "";
        for (const frame of frames) {
          let event = "message";
          const data = [];
          for (const line of frame.split(/\r?\n/)) {
            if (line.startsWith("event:")) event = line.slice(6).trim();
            if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
          }
          dispatch(event, data.join("\n"));
        }
        if (done) break;
      }
      if (!closed) dispatch("error");
      clearTimeout(timeoutId);
    } catch (error) {
      clearTimeout(timeoutId);
      if (!closed && error.name !== "AbortError") {
        const code = error.name === "TimeoutError" ? "timeout" : "network";
        dispatch("error", JSON.stringify({ code, message: error.message }));
      }
    }
  });
  return source;
}

function start() {
  if (state.source) return;

  const value = el("email").value.trim();
  if (!value) {
    toast(t(state.mode === "phone" ? "enterPhone" : "enterEmail"), true);
    el("email").focus();
    return;
  }
  state.results = [];
  state.email = value;
  state.activeStatuses = new Set();
  state.keyword = "";
  el("keyword").value = "";

  el("results").innerHTML = "";
  el("results-panel").hidden = true;
  el("stats").hidden = true;
  el("ai-report-panel").hidden = true;
  el("progress-panel").hidden = false;
  el("progress-bar").style.width = "0%";
  el("progress-text").textContent = t("connecting");
  el("progress-count").textContent = "0 / 0";
  setRunning(true);

  if (state.mode === "ai") {
    startAi(value);
    return;
  }

  const phoneMode = state.mode === "phone";
  const source = createPostEventStream(phoneMode ? "/api/phone-scan/stream" : "/api/scan/stream", {
    ...(phoneMode ? { phone: value } : { email: value }),
    consent: true,
    profile: state.scanProfile,
    only: [],
    exclude: [],
  });
  state.source = source;

  source.addEventListener("start", (e) => {
    const data = JSON.parse(e.data);
    state.total = data.total;
    const profileLabel = (data.profile || state.scanProfile) === "full" ? t("extendedLabel") : t("reliableLabel");
    const target = data.phone || data.email || state.email;
    el("progress-text").textContent = `${profileLabel} · ${t("scanning")} ${target}`;
    el("progress-count").textContent = `0 / ${data.total}`;
    if (data.total === 0) {
      el("progress-text").textContent = t("emptyScan");
      el("empty").textContent = t("emptyScan");
      el("empty").hidden = false;
    }
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
    el("progress-text").textContent = `${t("scanComplete")} · ${t("elapsed")} ${(summary.elapsed_ms / 1000).toFixed(1)} ${t("seconds")}`;
    el("progress-bar").style.width = "100%";
    if (!summary.total) {
      el("results-panel").hidden = true;
      el("empty").textContent = t("emptyScan");
      el("empty").hidden = false;
    }
    stop();
    renderStats(summary);
  });

  source.addEventListener("error", (e) => {
    const payload = parseStreamError(e.data);
    toast(formatStreamError(payload), true);
    el("progress-text").textContent = t("interrupted");
    el("progress-count").textContent = `${state.results.length} / ${state.total || 0}`;
    stop();
  });
}

function parseStreamError(data) {
  if (!data) return { code: "network" };
  try {
    return JSON.parse(data);
  } catch {
    return { code: "backend_error", message: data };
  }
}

function formatStreamError(payload) {
  const labels = {
    invalid_phone: "invalidPhone",
    auth_failure: "authFailure",
    rate_limited: "rateLimitFailure",
    timeout: "timeoutFailure",
    cors: "corsFailure",
    network: "connectionInterrupted",
  };
  const localized = labels[payload.code] ? t(labels[payload.code]) : null;
  return localized || payload.message || t("serverError");
}

function startAi(email) {
  const source = createPostEventStream("/api/ai/investigate", {
    email,
    consent: true,
    lang: state.lang,
  });
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
    const profileLabel = d.profile === "full" ? t("extendedTier") : t("reliableTier");
    el("progress-text").textContent = `${profileLabel} · ${t("aiAggregating")} · ${d.model}`;
    el("progress-count").textContent = "…";
    appendLog(`${t("model")} ${d.model}`);
    appendLog(`${t("tier")}: ${profileLabel} (SEEK_AI_PROFILE=${d.profile || "reliable"})`);
  });

  source.addEventListener("aggregate_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = t("runningTools");
    appendLog(`${t("startingBackends")}: ${(d.backends || []).join(", ")}`);
  });

  source.addEventListener("backend_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `${t("toolRunning")} · ${d.name}`;
    appendLog(`▶ ${d.name} (${d.modules || "?"} ${t("modules")})`);
  });

  source.addEventListener("backend_done", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`✓ ${d.name} ${t("completed")} ${JSON.stringify(d).slice(0, 120)}`);
  });

  source.addEventListener("backend_skip", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`○ ${t("skipped")} ${d.name}: ${d.reason || ""}`);
  });

  source.addEventListener("aggregate_done", (e) => {
    const d = JSON.parse(e.data);
    const s = d.stats || {};
    el("progress-bar").style.width = "55%";
    el("progress-text").textContent =
      `${t("aggregateComplete")} · ${t("effective")} ${s.effective ?? "?"} · ${t("registered")} ${s.registered ?? d.merged_registered_count ?? 0}`;
    appendLog(
      `${t("aggregateComplete")}: ${t("effective")} ${s.effective ?? "?"} / ${t("registered")} ${s.registered ?? 0} / ${t("notRegistered")} ${s.not_registered ?? 0} / ${t("intel")} ${s.intel ?? 0}`
    );
  });

  source.addEventListener("ai_thinking", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `${t("aiSummarizing")} · ${d.round}/${d.max}`;
    el("progress-bar").style.width = `${Math.min(95, 55 + d.round * 8)}%`;
    appendLog(`${t("aiSummarizing")} · ${t("round")} ${d.round}`);
  });

  source.addEventListener("ai_tool", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`${t("callingTool")} ${d.name}`);
    el("progress-text").textContent = `${t("callingTool")} · ${d.name}`;
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
    el("progress-text").textContent = t("aiComplete");
    el("progress-bar").style.width = "100%";
    stop();
  });

  source.addEventListener("error", (e) => {
    if (e.data) {
      try {
        toast(localizeDetail(JSON.parse(e.data).message, "error"), true);
      } catch {
        toast(t("aiError"), true);
      }
    } else if (!state.results.length) {
      toast(t("aiDisconnected"), true);
    }
    el("progress-text").textContent = t("interrupted");
    stop();
  });
}

function renderAiReport(report) {
  el("ai-report-panel").hidden = false;
  el("ai-summary").textContent = report.summary || "";

  const stats = report.stats || {};
  const statsBox = el("ai-stats");
  const cells = [
    ["effective", t("effective"), "ok"],
    ["registered", t("registered"), ""],
    ["not_registered", t("notRegistered"), ""],
    ["intel", t("intel"), ""],
    ["failed", t("failedUnknown"), "warn"],
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
        a.textContent = ` ${t("open")}`;
        a.style.color = "var(--accent)";
        li.appendChild(a);
      }
      box.appendChild(li);
    });
    if (!(items || []).length) {
      box.innerHTML = `<li><small>${t("none")}</small></li>`;
    }
  };
  fill("ai-confirmed", report.confirmed);
  fill("ai-intel", report.intel);
  fill("ai-not-registered", report.not_registered);
  fill("ai-likely", report.likely);
  const next = el("ai-next");
  if (report.next_steps && report.next_steps.length) {
    next.innerHTML =
      `<strong>${t("nextSteps")}</strong><ol>` +
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
  const idle = state.mode === "ai" ? t("startAi") : state.mode === "phone" ? t("startPhone") :
    state.scanProfile === "full" ? t("startExtended") : t("startQuery");
  el("run").querySelector(".btn-label").textContent = running ? t("running") : idle;
  el("stop").hidden = !running;
}

/* ---------------- 渲染 ---------------- */
const STATUS_ORDER = ["registered", "info", "unknown", "rate_limited", "not_registered", "error", "skipped"];
const CATEGORY_ORDER = [
  "domain", "mail", "breach", "profile", "social", "forum", "crm",
  "dev", "edu", "jobs", "shop", "payment", "crowdfunding", "media",
  "music", "sport", "transport", "medical", "realestate", "osint",
  "adult", "other",
];

function categoryRank(category) {
  const index = CATEGORY_ORDER.indexOf(category);
  return index < 0 ? CATEGORY_ORDER.length : index;
}

function render() {
  renderStatusFilters();
  const box = el("results");
  const rows = state.results
    .filter((r) => !state.activeStatuses.size || state.activeStatuses.has(r.status))
    .filter((r) => !state.keyword || `${r.title} ${localizeTitle(r.title)} ${r.provider}`.toLowerCase().includes(state.keyword))
    .sort(
      (a, b) =>
        categoryRank(a.category) - categoryRank(b.category) ||
        (CATEGORY_LABEL[a.category] || a.category).localeCompare(
          CATEGORY_LABEL[b.category] || b.category,
          "zh"
        ) ||
        STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status) ||
        a.title.localeCompare(b.title, "zh")
    );

  box.innerHTML = "";
  const groups = new Map();
  rows.forEach((r) => {
    const category = r.category || "other";
    if (!groups.has(category)) groups.set(category, []);
    groups.get(category).push(r);
  });
  groups.forEach((groupRows, category) => {
    const group = document.createElement("section");
    group.className = "result-group";

    const header = document.createElement("div");
    header.className = "result-group-header";
    const label = document.createElement("span");
    label.className = "result-group-title";
    label.textContent = CATEGORY_LABEL[category] || category;
    const count = document.createElement("span");
    count.className = "result-group-count";
    count.textContent = String(groupRows.length);
    header.append(label, count);
    group.appendChild(header);

    const groupRowsBox = document.createElement("div");
    groupRowsBox.className = "result-group-rows";
    groupRows.forEach((r) => groupRowsBox.appendChild(rowNode(r)));
    group.appendChild(groupRowsBox);
    box.appendChild(group);
  });
  el("empty").hidden = rows.length > 0;
}

function rowNode(r) {
  const row = document.createElement("div");
  row.className = "row";

  const badge = document.createElement("span");
  badge.className = `badge ${r.status}`;
  badge.textContent = STATUS_LABEL[r.status] || r.status;
  row.appendChild(badge);

  const avatarUrl = safeHttpUrl(r.data && r.data.avatar_url);
  if (avatarUrl) {
    const avatarLink = document.createElement("a");
    avatarLink.className = "row-avatar-link";
    avatarLink.href = avatarUrl;
    avatarLink.target = "_blank";
    avatarLink.rel = "noreferrer noopener";
    avatarLink.title = t("viewPublicAvatar");
    const avatar = document.createElement("img");
    avatar.className = "row-avatar";
    avatar.src = avatarUrl;
    avatar.alt = `${localizeTitle(r.title)} avatar`;
    avatar.loading = "lazy";
    avatar.referrerPolicy = "no-referrer";
    avatar.addEventListener("error", () => avatarLink.remove());
    avatarLink.appendChild(avatar);
    row.appendChild(avatarLink);
  }

  const main = document.createElement("div");
  main.className = "row-main";

  const title = document.createElement("div");
  title.className = "row-title";
  if (r.homepage) {
    const link = document.createElement("a");
    link.href = r.homepage;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    link.textContent = localizeTitle(r.title);
    title.appendChild(link);
  } else {
    const name = document.createElement("span");
    name.className = "name";
    name.textContent = localizeTitle(r.title);
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
    detail.textContent = localizeDetail(r.detail, r.status);
    main.appendChild(detail);
  }

  const entries = Object.entries(r.data || {}).filter(([k]) => k !== "avatar_url");
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
      appendDataValue(val, v);
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

function safeHttpUrl(value) {
  if (typeof value !== "string") return null;
  try {
    const url = new URL(value, window.location.href);
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : null;
  } catch {
    return null;
  }
}

function appendDataValue(container, value) {
  if (Array.isArray(value)) {
    container.textContent = value.join(", ");
    return;
  }
  if (value && typeof value === "object") {
    container.textContent = JSON.stringify(value, null, 2);
    container.classList.add("is-json");
    return;
  }
  const url = safeHttpUrl(value);
  if (url) {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    link.textContent = value;
    container.appendChild(link);
    return;
  }
  if (typeof value === "boolean") {
    container.textContent = value ? t("yes") : t("no");
    return;
  }
  container.textContent = value == null ? "-" : String(value);
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
    { key: "registered", label: STATUS_LABEL.registered, cls: "is-registered" },
    { key: "info", label: STATUS_LABEL.info, cls: "is-info" },
    { key: "unknown", label: STATUS_LABEL.unknown, cls: "is-unknown" },
    { key: "not_registered", label: STATUS_LABEL.not_registered, cls: "" },
    { key: "error", label: state.lang === "en" ? "Failed / rate limited" : "失败/限流", cls: "is-error", extra: "rate_limited" },
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
  if (!state.results.length) return toast(t("noResultsExport"), true);
  download(
    `seek_${slug()}.json`,
    JSON.stringify({
      email: state.email,
      profile: state.mode === "ai" ? "ai" : state.scanProfile,
      generated_at: new Date().toISOString(),
      results: state.results,
    }, null, 2),
    "application/json"
  );
}

function exportCsv() {
  if (!state.results.length) return toast(t("noResultsExport"), true);
  const header = state.lang === "en"
    ? ["Site", "Provider", "Category", "Status", "Detail", "HTTP", "Elapsed (ms)", "Additional data"]
    : ["站点", "标识", "分类", "状态", "说明", "HTTP", "耗时(ms)", "附加数据"];
  const escape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = [header.map(escape).join(",")];
  state.results.forEach((r) => {
    lines.push(
      [
        localizeTitle(r.title),
        r.provider,
        CATEGORY_LABEL[r.category] || r.category,
        STATUS_LABEL[r.status] || r.status,
        localizeDetail(r.detail, r.status) || "",
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
