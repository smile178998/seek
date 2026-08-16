// Translations for core UI strings and status labels (34 languages)
const TRANSLATIONS = {
  en: {
    title: "Seek · Email registration footprint lookup",
    brandSub: "Email registration footprint lookup",
    apiDocs: "API Docs",
    languageLabel: "Language",
    all: "All",
    emailPlaceholder: "somebody@example.com",
    run_default: "Start scan",
    run_ai: "Start AI summary",
    run_full: "Start extended scan",
    stop: "Stop",
    mode_reliable: "Reliable scan",
    mode_full: "Extended scan",
    mode_ai: "AI summary",
    hint_reliable: "Reliable: only verified modules, faster",
    hint_full: "Extended: covers more candidates, slower",
    progress_connecting: "Connecting…",
    scan_complete: "Scan complete",
    profile_reliable: "Reliable",
    profile_full: "Extended",
    ai_aggregating: "Aggregating results",
    ai_model: "Model",
    ai_profile: "Profile",
    ai_backends_started: "Backends started",
    ai_backend_running: "Running backend",
    ai_backend_done: "Backend finished",
    ai_backend_skipped: "Backend skipped",
    ai_aggregate_summary: "Scan complete summary",
    running_tools: "Running detection tools…",
    ai_thinking: "AI summarizing",
    ai_done: "AI investigation complete",
    ai_error: "AI investigation error",
    ai_connection_interrupted: "AI connection interrupted, ensure API Key configured and restart",
    export_json: "Export JSON",
    export_csv: "Export CSV",
    filter_placeholder: "Filter sites…",
    ai_report_title: "AI Summary Report",
    ai_confirmed: "Confirmed Registered",
    ai_intel: "Domain / Email Intel",
    ai_not_registered: "Confirmed Not Registered",
    ai_likely: "Likely Leads",
    no_results: "No results matching filters",
    in_progress: "Detecting…",
    yes: "Yes",
    no: "No",
    notice_title: "Usage notes",
    notice_li_1: "This tool is for personal asset review and authorized assessments only.",
    notice_li_2: "Results are inference: site changes, rate-limiting, and CDN caches may cause false positives/negatives.",
    notice_li_3: "Reliable scans run verified high-availability modules; extended scans include more candidates and may be slower.",
    notice_li_4: "Modules only use public site interfaces. Add definitions under seek/definitions/ if needed and verify legality.",
    view_public_avatar: "View public avatar",
    public_avatar: "public avatar",
    open: "Open",
    no_results_export: "No results to export",
    csv_header_site: "Site",
    csv_header_id: "Identifier",
    csv_header_category: "Category",
    csv_header_status: "Status",
    csv_header_detail: "Detail",
    csv_header_http: "HTTP",
    csv_header_elapsed: "Elapsed(ms)",
    csv_header_data: "Extra Data",
    categories: {
      social: "Social",
      shop: "E-commerce",
      dev: "Dev",
      profile: "Profile",
      breach: "Breach DB",
      domain: "Domain",
      mail: "Email",
      music: "Music",
      media: "Media",
      forum: "Forum",
      crm: "CRM",
      payment: "Payment",
      crowdfunding: "Crowdfunding",
      adult: "Adult",
      osint: "OSINT",
      edu: "Education",
      jobs: "Jobs",
      medical: "Medical",
      sport: "Sports",
      transport: "Transport",
      realestate: "Real Estate",
      other: "Other",
    },
    data_labels: {
      username: "Username",
      display_name: "Display name",
      profile_url: "Profile URL",
      avatar_url: "Avatar",
      user_id: "User ID",
      name: "Name",
      streak: "Streak",
      has_plus: "Has paid",
      has_google_id: "Has Google",
      has_facebook_id: "Has Facebook",
      location: "Location",
      accounts: "Accounts",
      urls: "Links",
      breaches: "Breaches",
      breach_dates: "Breach dates",
      mx: "MX records",
      providers: "Providers",
      disposable: "Disposable",
      masked_phone: "Masked phone",
      masked_email: "Masked email",
    },
    toast_connect_error: "Cannot connect to backend: ",
    toast_enter_email: "Please enter an email to scan",
    toast_config_ai: "Please configure SEEK_AI_API_KEY in .env and restart",
    toast_start_failed: "Failed to start scan: ",
    status: {
      registered: "Registered",
      not_registered: "Not registered",
      info: "Info",
      unknown: "Unknown",
      rate_limited: "Rate limited",
      error: "Error",
      skipped: "Skipped",
    },
    none: "None",
    next_steps_title: "Suggested next steps",
    stats_effective: "Effective",
    ai_round_label: "AI round",
    ai_tool_calling: "Calling tool",
    ai_tool_running: "AI calling tool",
  },
  zh: {
    title: "Seek · 邮箱注册痕迹反查",
    brandSub: "邮箱注册痕迹反查",
    apiDocs: "API 文档",
    languageLabel: "语言",
    all: "所有",
    emailPlaceholder: "somebody@example.com",
    run_default: "开始查询",
    run_ai: "开始 AI 汇总",
    run_full: "开始扩展查询",
    stop: "停止",
    mode_reliable: "可靠扫描",
    mode_full: "扩展扫描",
    mode_ai: "AI 可靠汇总",
    hint_reliable: "可靠扫描：仅运行已验证站点，速度更快",
    hint_full: "扩展扫描：覆盖更多候选站点，耗时和受限结果会增加",
    progress_connecting: "正在建立连接…",
    scan_complete: "检测完成",
    profile_reliable: "可靠",
    profile_full: "完整",
    ai_aggregating: "检测聚合中",
    running_tools: "正在运行可靠检测工具…",
    ai_thinking: "AI 汇总中",
    export_json: "导出 JSON",
    export_csv: "导出 CSV",
    filter_placeholder: "过滤站点…",
    ai_report_title: "AI 汇总报告",
    ai_confirmed: "已确认注册",
    ai_intel: "域名 / 邮箱情报",
    ai_not_registered: "明确未注册",
    ai_likely: "疑似线索",
    no_results: "没有符合当前筛选条件的结果",
    in_progress: "检测中…",
    yes: "是",
    no: "否",
    notice_title: "使用须知",
    notice_li_1: "本工具仅用于本人账号资产梳理与已授权的安全评估。未经授权针对他人查询可能违法。",
    notice_li_2: "结果仅为探测推断：站点改版、风控拦截、CDN 缓存都可能造成误报或漏报。",
    notice_li_3: "可靠扫描仅运行已验证的高可用模块；扩展扫描会加入更多候选规则，但更慢，也更容易受限。",
    notice_li_4: "内置模块只使用站点官方公开提供的查询接口。如需扩展，请在 seek/definitions/ 下添加规则并确认合法性。",
    view_public_avatar: "查看公开头像",
    public_avatar: "公开头像",
    open: "打开",
    no_results_export: "暂无结果可导出",
    csv_header_site: "站点",
    csv_header_id: "标识",
    csv_header_category: "分类",
    csv_header_status: "状态",
    csv_header_detail: "说明",
    csv_header_http: "HTTP",
    csv_header_elapsed: "耗时(ms)",
    csv_header_data: "附加数据",
    categories: {
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
    },
    data_labels: {
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
    },
    toast_connect_error: "无法连接后端服务：",
    toast_enter_email: "请输入要查询的邮箱",
    toast_config_ai: "请先在 .env 配置 SEEK_AI_API_KEY 并重启服务",
    toast_start_failed: "启动查询失败：",
    toast_server_error: "服务端返回了错误",
    toast_connection_interrupted: "连接中断，请检查邮箱格式、授权勾选或访问频率限制",
    status_interrupted: "已中断",
    none: "暂无",
    next_steps_title: "建议下一步",
    stats_effective: "有效",
    ai_round_label: "AI 汇总轮次",
    ai_tool_calling: "调用工具",
    ai_tool_running: "AI 调用工具",
    status: {
      registered: "已注册",
      not_registered: "未注册",
      info: "情报",
      unknown: "无法判定",
      rate_limited: "被限流",
      error: "失败",
      skipped: "跳过",
    },
  },
  // Minimal translations for additional languages. Use English fallbacks when missing.
  es: { languageLabel: "Idioma", all: "Todos", emailPlaceholder: "somebody@example.com", run_default: "Iniciar búsqueda", export_json: "Exportar JSON", export_csv: "Exportar CSV", filter_placeholder: "Filtrar sitios…", toast_enter_email: "Por favor ingrese un correo electrónico", notice_title: "Notas de uso", notice_li_1: "Esta herramienta es para revisión de activos personales y evaluaciones autorizadas.", notice_li_2: "Los resultados son inferencias: cambios del sitio, limitaciones y cachés CDN pueden causar falsos positivos/negativos.", notice_li_3: "El escaneo confiable usa módulos verificados; el escaneo extendido incluye más candidatos y puede ser más lento.", notice_li_4: "Los módulos usan solo interfaces públicas. Para ampliar, añada definiciones en seek/definitions/ y verifique la legalidad.", status: { registered: "Registrado", not_registered: "No registrado", info: "Info", unknown: "Desconocido", rate_limited: "Limitado", error: "Error", skipped: "Omitido" } },
  fr: {
    title: "Seek · Recherche d'empreinte d'inscription par e-mail",
    brandSub: "Recherche d'empreinte d'inscription par e-mail",
    apiDocs: "Docs API",
    languageLabel: "Langue",
    all: "Tous",
    emailPlaceholder: "somebody@example.com",
    run_default: "Démarrer la recherche",
    run_ai: "Démarrer le résumé IA",
    run_full: "Démarrer l'analyse étendue",
    stop: "Arrêter",
    mode_reliable: "Analyse fiable",
    mode_full: "Analyse étendue",
    mode_ai: "Résumé IA",
    hint_reliable: "Fiable : uniquement modules vérifiés, plus rapide",
    hint_full: "Étendue : couvre plus de candidats, plus lent",
    progress_connecting: "Connexion…",
    scan_complete: "Analyse terminée",
    profile_reliable: "Fiable",
    profile_full: "Étendue",
    ai_aggregating: "Agrégation des résultats",
    running_tools: "Exécution des outils…",
    ai_thinking: "IA en cours",
    ai_model: "Modèle",
    ai_profile: "Profil",
    ai_backends_started: "Backends démarrés",
    ai_backend_running: "Backend en cours",
    ai_backend_done: "Backend terminé",
    ai_backend_skipped: "Backend ignoré",
    ai_aggregate_summary: "Résumé de l'analyse",
    ai_done: "Analyse IA terminée",
    ai_error: "Erreur IA",
    ai_connection_interrupted: "Connexion IA interrompue, vérifiez la clé API et redémarrez",
    export_json: "Exporter JSON",
    export_csv: "Exporter CSV",
    filter_placeholder: "Filtrer les sites…",
    ai_report_title: "Rapport résumé IA",
    ai_confirmed: "Confirmés",
    ai_intel: "Domaine / Infos e-mail",
    ai_not_registered: "Confirmé non enregistré",
    ai_likely: "Pistes probables",
    no_results: "Aucun résultat correspondant aux filtres",
    in_progress: "En cours…",
    yes: "Oui",
    no: "Non",
    notice_title: "Notes d'utilisation",
    notice_li_1: "Cet outil est réservé à l'examen d'actifs personnels et aux évaluations autorisées.",
    notice_li_2: "Les résultats sont des inférences : changements de site, limitations et caches CDN peuvent produire des faux positifs/négatifs.",
    notice_li_3: "Analyse fiable : modules vérifiés ; analyse étendue : plus de candidats, plus lente.",
    notice_li_4: "Les modules utilisent uniquement des interfaces publiques. Pour étendre, ajoutez des définitions sous seek/definitions/ et vérifiez la légalité.",
    view_public_avatar: "Voir l'avatar public",
    public_avatar: "avatar public",
    open: "Ouvrir",
    no_results_export: "Aucun résultat à exporter",
    csv_header_site: "Site",
    csv_header_id: "Identifiant",
    csv_header_category: "Catégorie",
    csv_header_status: "Statut",
    csv_header_detail: "Détail",
    csv_header_http: "HTTP",
    csv_header_elapsed: "Durée(ms)",
    csv_header_data: "Données",
    toast_connect_error: "Impossible de joindre le serveur : ",
    toast_enter_email: "Veuillez entrer un e-mail",
    toast_config_ai: "Veuillez configurer SEEK_AI_API_KEY dans .env et redémarrer",
    toast_start_failed: "Échec du démarrage : ",
    toast_server_error: "Le serveur a retourné une erreur",
    toast_connection_interrupted: "Connexion interrompue, vérifiez l'e-mail, le consentement ou les limites de fréquence",
    status_interrupted: "Interrompu",
    status: { registered: "Enregistré", not_registered: "Non enregistré", info: "Info", unknown: "Inconnu", rate_limited: "Limité", error: "Erreur", skipped: "Ignoré" },
    categories: {
      social: "Social",
      shop: "E-commerce",
      dev: "Dev",
      profile: "Profil",
      breach: "Base de fuites",
      domain: "Domaine",
      mail: "Email",
      music: "Musique",
      media: "Média",
      forum: "Forum",
      crm: "CRM",
      payment: "Paiement",
      crowdfunding: "Financement participatif",
      adult: "Adulte",
      osint: "OSINT",
      edu: "Éducation",
      jobs: "Emplois",
      medical: "Médical",
      sport: "Sport",
      transport: "Transport",
      realestate: "Immobilier",
      other: "Autre",
    },
    data_labels: {
      username: "Nom d'utilisateur",
      display_name: "Nom affiché",
      profile_url: "URL du profil",
      avatar_url: "Avatar",
      user_id: "ID utilisateur",
      name: "Nom",
      streak: "Série",
      has_plus: "Abonné",
      has_google_id: "A Google",
      has_facebook_id: "A Facebook",
      location: "Lieu",
      accounts: "Comptes",
      urls: "Liens",
      breaches: "Fuites",
      breach_dates: "Dates",
      mx: "Enregistrements MX",
      providers: "Fournisseurs",
      disposable: "Jetable",
      masked_phone: "Téléphone masqué",
      masked_email: "Email masqué",
    },
    none: "Aucun",
    next_steps_title: "Étapes suggérées",
    stats_effective: "Effectif",
    ai_round_label: "Tour IA",
    ai_tool_calling: "Appel d'outil",
    ai_tool_running: "IA appelant l'outil",
  },
  de: { languageLabel: "Sprache", all: "Alle", emailPlaceholder: "somebody@example.com", run_default: "Suche starten", export_json: "Exportieren JSON", export_csv: "Exportieren CSV", filter_placeholder: "Filter Sites…", toast_enter_email: "Bitte E-Mail eingeben", notice_title: "Hinweise zur Verwendung", notice_li_1: "Dieses Tool dient nur zur Überprüfung eigener Konten und autorisierten Bewertungen.", notice_li_2: "Ergebnisse sind Schlussfolgerungen: Webseitenänderungen, Sperren oder CDN-Caches können zu Fehlern führen.", notice_li_3: "Zuverlässiger Scan verwendet verifizierte Module; erweiterter Scan durchsucht mehr Kandidaten und ist langsamer.", notice_li_4: "Module nutzen nur öffentliche Schnittstellen. Zur Erweiterung Definitionsdateien unter seek/definitions/ hinzufügen und Rechtslage prüfen.", status: { registered: "Registriert", not_registered: "Nicht registriert", info: "Info", unknown: "Unbekannt", rate_limited: "Begrenzt", error: "Fehler", skipped: "Übersprungen" } },
  ja: { languageLabel: "言語", all: "すべて", emailPlaceholder: "somebody@example.com", run_default: "検索開始", export_json: "JSON をエクスポート", export_csv: "CSV をエクスポート", filter_placeholder: "サイトを絞り込む…", toast_enter_email: "メールアドレスを入力してください", notice_title: "使用上の注意", notice_li_1: "本ツールは本人のアカウント確認および許可された評価のためのものです。", notice_li_2: "結果は推測です：サイト変更、レート制限、CDNキャッシュにより誤検知が発生する可能性があります。", notice_li_3: "信頼スキャンは検証済モジュールを使用し、高速です；拡張スキャンは候補が増え遅くなる場合があります。", notice_li_4: "組み込みモジュールは公開インターフェースのみを使用します。拡張は seek/definitions/ に追加してください。", status: { registered: "登録済み", not_registered: "未登録", info: "情報", unknown: "不明", rate_limited: "制限", error: "エラー", skipped: "スキップ" } },
  ko: { languageLabel: "언어", all: "모두", emailPlaceholder: "somebody@example.com", run_default: "검색 시작", export_json: "JSON 내보내기", export_csv: "CSV 내보내기", filter_placeholder: "사이트 필터…", toast_enter_email: "이메일을 입력하세요", notice_title: "사용 시 주의사항", notice_li_1: "이 도구는 본인 계정 자산 검토 및 승인된 평가용입니다.", notice_li_2: "결과는 추정입니다: 사이트 변경, 제한, CDN 캐시로 인해 오탐/누락이 발생할 수 있습니다.", notice_li_3: "신뢰 스캔은 검증된 모듈만 사용; 확장 스캔은 더 많은 후보를 포함합니다.", notice_li_4: "내장 모듈은 공개 인터페이스만 사용합니다. 확장 시 seek/definitions/에 추가하세요.", status: { registered: "등록됨", not_registered: "등록되지 않음", info: "정보", unknown: "알 수 없음", rate_limited: "제한됨", error: "오류", skipped: "건너뜀" } },
  ru: { languageLabel: "Язык", all: "Все", emailPlaceholder: "somebody@example.com", run_default: "Запустить проверку", export_json: "Экспорт JSON", export_csv: "Экспорт CSV", filter_placeholder: "Фильтр сайтов…", toast_enter_email: "Пожалуйста, введите email", notice_title: "Примечания по использованию", notice_li_1: "Этот инструмент предназначен для проверки собственных аккаунтов и авторизованных оценок.", notice_li_2: "Результаты — предположения: изменения сайта, ограничения или кеши CDN могут вызвать ошибки.", notice_li_3: "Надежное сканирование использует проверенные модули; расширенное — больше кандидатов, медленнее.", notice_li_4: "Модули используют только публичные интерфейсы. Для расширения добавьте определения в seek/definitions/.", status: { registered: "Зарегистрирован", not_registered: "Не зарегистрирован", info: "Инфо", unknown: "Неизвестно", rate_limited: "Ограничено", error: "Ошибка", skipped: "Пропущено" } },
  pt: { languageLabel: "Idioma", all: "Todos", emailPlaceholder: "somebody@example.com", run_default: "Iniciar busca", export_json: "Exportar JSON", export_csv: "Exportar CSV", filter_placeholder: "Filtrar sites…", toast_enter_email: "Por favor insira um email", notice_title: "Notas de uso", notice_li_1: "Esta ferramenta é para revisão de ativos pessoais e avaliações autorizadas.", notice_li_2: "Resultados são inferências: mudanças no site, limitações e caches CDN podem causar falsos positivos/negativos.", notice_li_3: "Varredura confiável usa módulos verificados; varredura estendida inclui mais candidatos e pode ser mais lenta.", notice_li_4: "Módulos usam apenas interfaces públicas. Para estender, adicione definições em seek/definitions/ e verifique a legalidade.", status: { registered: "Registrado", not_registered: "Não registrado", info: "Info", unknown: "Desconhecido", rate_limited: "Limitado", error: "Erro", skipped: "Ignorado" } },
  ar: { languageLabel: "اللغة", all: "الكل", emailPlaceholder: "somebody@example.com", run_default: "ابدأ الفحص", export_json: "تصدير JSON", export_csv: "تصدير CSV", filter_placeholder: "تصفية المواقع…", toast_enter_email: "الرجاء إدخال البريد الإلكتروني", notice_title: "ملاحظات الاستخدام", notice_li_1: "هذه الأداة لمراجعة أصول الحساب الشخصي والتقييمات المصرح بها فقط.", notice_li_2: "النتائج استنتاجات: تغييرات الموقع أو قيود السرعة أو ذاكرة CDN قد تؤدي إلى أخطاء.", notice_li_3: "الفحص الموثوق يستخدم وحدات مُتحققة؛ الفحص الموسع يشمل مرشحين أكثر ويكون أبطأ.", notice_li_4: "الوحدات المضمنة تستخدم واجهات عامة فقط. لإضافة، ضع ملفات التعريف في seek/definitions/ وتحقق من الشرعية.", status: { registered: "مسجل", not_registered: "غير مسجل", info: "معلومات", unknown: "غير معروف", rate_limited: "محدد", error: "خطأ", skipped: "تخطى" } },
  it: { languageLabel: "Lingua", all: "Tutti", emailPlaceholder: "somebody@example.com", run_default: "Avvia scansione", export_json: "Esporta JSON", export_csv: "Esporta CSV", filter_placeholder: "Filtra siti…", toast_enter_email: "Inserisci un'email", status: { registered: "Registrato", not_registered: "Non registrato", info: "Info", unknown: "Sconosciuto", rate_limited: "Limitato", error: "Errore", skipped: "Saltato" } },
  nl: { languageLabel: "Taal", all: "Alle", emailPlaceholder: "somebody@example.com", run_default: "Zoek starten", export_json: "Exporteer JSON", export_csv: "Exporteer CSV", filter_placeholder: "Filter sites…", toast_enter_email: "Voer een e-mail in", status: { registered: "Geregistreerd", not_registered: "Niet geregistreerd", info: "Info", unknown: "Onbekend", rate_limited: "Beperkt", error: "Fout", skipped: "Overgeslagen" } },
  sv: { languageLabel: "Språk", all: "Alla", emailPlaceholder: "somebody@example.com", run_default: "Starta sökning", export_json: "Exportera JSON", export_csv: "Exportera CSV", filter_placeholder: "Filtrera platser…", toast_enter_email: "Ange en e-postadress", status: { registered: "Registrerad", not_registered: "Inte registrerad", info: "Info", unknown: "Okänt", rate_limited: "Begränsad", error: "Fel", skipped: "Hoppad" } },
  no: { languageLabel: "Språk", all: "Alle", emailPlaceholder: "somebody@example.com", run_default: "Start søk", export_json: "Eksporter JSON", export_csv: "Eksporter CSV", filter_placeholder: "Filtrer nettsteder…", toast_enter_email: "Vennligst oppgi e-post", status: { registered: "Registrert", not_registered: "Ikke registrert", info: "Info", unknown: "Ukjent", rate_limited: "Begrenset", error: "Feil", skipped: "Hoppet over" } },
  da: { languageLabel: "Sprog", all: "Alle", emailPlaceholder: "somebody@example.com", run_default: "Start søgning", export_json: "Eksporter JSON", export_csv: "Eksporter CSV", filter_placeholder: "Filtrer sider…", toast_enter_email: "Indtast en e-mail", status: { registered: "Registreret", not_registered: "Ikke registreret", info: "Info", unknown: "Ukendt", rate_limited: "Begrænset", error: "Fejl", skipped: "Sprunget over" } },
  fi: { languageLabel: "Kieli", all: "Kaikki", emailPlaceholder: "somebody@example.com", run_default: "Aloita haku", export_json: "Vie JSON", export_csv: "Vie CSV", filter_placeholder: "Suodata sivuja…", toast_enter_email: "Anna sähköposti", status: { registered: "Rekisteröity", not_registered: "Ei rekisteröity", info: "Tieto", unknown: "Tuntematon", rate_limited: "Rajoitettu", error: "Virhe", skipped: "Ohitettu" } },
  pl: { languageLabel: "Język", all: "Wszystkie", emailPlaceholder: "somebody@example.com", run_default: "Rozpocznij skan", export_json: "Eksportuj JSON", export_csv: "Eksportuj CSV", filter_placeholder: "Filtruj serwisy…", toast_enter_email: "Wprowadź adres e-mail", status: { registered: "Zarejestrowany", not_registered: "Nie zarejestrowany", info: "Info", unknown: "Nieznany", rate_limited: "Ograniczony", error: "Błąd", skipped: "Pominięto" } },
  cs: { languageLabel: "Jazyk", all: "Všechny", emailPlaceholder: "somebody@example.com", run_default: "Spustit kontrolu", export_json: "Exportovat JSON", export_csv: "Exportovat CSV", filter_placeholder: "Filtrovat stránky…", toast_enter_email: "Zadejte e-mail", status: { registered: "Registrováno", not_registered: "Neregistrováno", info: "Info", unknown: "Neznámé", rate_limited: "Omezeno", error: "Chyba", skipped: "Přeskočeno" } },
  hu: { languageLabel: "Nyelv", all: "Mind", emailPlaceholder: "somebody@example.com", run_default: "Indítás", export_json: "Export JSON", export_csv: "Export CSV", filter_placeholder: "Szűrés…", toast_enter_email: "Adjon meg egy e-mailt", status: { registered: "Regisztrált", not_registered: "Nincs regisztrálva", info: "Info", unknown: "Ismeretlen", rate_limited: "Korlátozott", error: "Hiba", skipped: "Kihagyva" } },
  tr: { languageLabel: "Dil", all: "Tüm", emailPlaceholder: "somebody@example.com", run_default: "Tarama başlat", export_json: "JSON dışa aktar", export_csv: "CSV dışa aktar", filter_placeholder: "Siteleri filtrele…", toast_enter_email: "Lütfen e-posta girin", status: { registered: "Kayıtlı", not_registered: "Kayıtlı değil", info: "Bilgi", unknown: "Bilinmiyor", rate_limited: "Sınırlandı", error: "Hata", skipped: "Atlandı" } },
  he: { languageLabel: "שפה", all: "הכל", emailPlaceholder: "somebody@example.com", run_default: "התחל סריקה", export_json: "ייצא JSON", export_csv: "ייצא CSV", filter_placeholder: "סינון אתרים…", toast_enter_email: "אנא הזן אימייל", status: { registered: "נרשם", not_registered: "לא רשום", info: "מידע", unknown: "לא ידוע", rate_limited: "מוגבל", error: "שגיאה", skipped: "דלג" } },
  id: { languageLabel: "Bahasa", all: "Semua", emailPlaceholder: "somebody@example.com", run_default: "Mulai pemindaian", export_json: "Ekspor JSON", export_csv: "Ekspor CSV", filter_placeholder: "Saring situs…", toast_enter_email: "Masukkan email", status: { registered: "Terdaftar", not_registered: "Tidak terdaftar", info: "Info", unknown: "Tidak diketahui", rate_limited: "Dibatasi", error: "Kesalahan", skipped: "Dilewati" } },
  vi: { languageLabel: "Ngôn ngữ", all: "Tất cả", emailPlaceholder: "somebody@example.com", run_default: "Bắt đầu quét", export_json: "Xuất JSON", export_csv: "Xuất CSV", filter_placeholder: "Lọc trang…", toast_enter_email: "Vui lòng nhập email", status: { registered: "Đã đăng ký", not_registered: "Chưa đăng ký", info: "Thông tin", unknown: "Không rõ", rate_limited: "Bị giới hạn", error: "Lỗi", skipped: "Bỏ qua" } },
  th: { languageLabel: "ภาษา", all: "ทั้งหมด", emailPlaceholder: "somebody@example.com", run_default: "เริ่มการค้นหา", export_json: "ส่งออก JSON", export_csv: "ส่งออก CSV", filter_placeholder: "กรองไซต์…", toast_enter_email: "กรุณาใส่อีเมล", status: { registered: "ลงทะเบียนแล้ว", not_registered: "ยังไม่ได้ลงทะเบียน", info: "ข้อมูล", unknown: "ไม่ทราบ", rate_limited: "จำกัด", error: "ข้อผิดพลาด", skipped: "ข้าม" } },
  ms: { languageLabel: "Bahasa", all: "Semua", emailPlaceholder: "somebody@example.com", run_default: "Mula imbasan", export_json: "Eksport JSON", export_csv: "Eksport CSV", filter_placeholder: "Tapis tapak…", toast_enter_email: "Sila masukkan e-mel", status: { registered: "Didaftar", not_registered: "Tidak didaftarkan", info: "Info", unknown: "Tidak diketahui", rate_limited: "Dihadkan", error: "Ralat", skipped: "Dilangkau" } },
  ro: { languageLabel: "Limbă", all: "Toate", emailPlaceholder: "somebody@example.com", run_default: "Pornește scanarea", export_json: "Exportă JSON", export_csv: "Exportă CSV", filter_placeholder: "Filtrează situri…", toast_enter_email: "Introduceți un email", status: { registered: "Înregistrat", not_registered: "Nere	gistrat", info: "Info", unknown: "Necunoscut", rate_limited: "Limitat", error: "Eroare", skipped: "Sărit" } },
  sk: { languageLabel: "Jazyk", all: "Všetky", emailPlaceholder: "somebody@example.com", run_default: "Spustiť kontrolu", export_json: "Exportovať JSON", export_csv: "Exportovať CSV", filter_placeholder: "Filtrovať stránky…", toast_enter_email: "Zadajte e-mail", status: { registered: "Registrované", not_registered: "Neregistrované", info: "Info", unknown: "Neznáme", rate_limited: "Obmedzené", error: "Chyba", skipped: "Preskočené" } },
  sr: { languageLabel: "Језик", all: "Сви", emailPlaceholder: "somebody@example.com", run_default: "Почни скенирање", export_json: "Извези JSON", export_csv: "Извези CSV", filter_placeholder: "Филтрирај сајтове…", toast_enter_email: "Унесите имејл", status: { registered: "Регистрован", not_registered: "Није регистровано", info: "Инфо", unknown: "Непознато", rate_limited: "Ограничено", error: "Грешка", skipped: "Прескочено" } },
  uk: { languageLabel: "Мова", all: "Усі", emailPlaceholder: "somebody@example.com", run_default: "Почати перевірку", export_json: "Експорт JSON", export_csv: "Експорт CSV", filter_placeholder: "Фільтрувати сайти…", toast_enter_email: "Введіть email", status: { registered: "Зареєстровано", not_registered: "Не зареєстровано", info: "Інфо", unknown: "Невідомо", rate_limited: "Обмежено", error: "Помилка", skipped: "Пропущено" } },
  bg: { languageLabel: "Език", all: "Всички", emailPlaceholder: "somebody@example.com", run_default: "Започни сканиране", export_json: "Експорт JSON", export_csv: "Експорт CSV", filter_placeholder: "Филтрирай сайтове…", toast_enter_email: "Въведете имейл", status: { registered: "Регистриран", not_registered: "Не е регистриран", info: "Инфо", unknown: "Неизвестно", rate_limited: "Ограничава се", error: "Грешка", skipped: "Пропуснато" } },
  el: { languageLabel: "Γλώσσα", all: "Όλα", emailPlaceholder: "somebody@example.com", run_default: "Έναρξη ελέγχου", export_json: "Εξαγωγή JSON", export_csv: "Εξαγωγή CSV", filter_placeholder: "Φιλτράρισμα ιστότοπων…", toast_enter_email: "Εισάγετε ένα email", status: { registered: "Εγγεγραμμένο", not_registered: "Μη εγγεγραμμένο", info: "Πληροφορία", unknown: "Άγνωστο", rate_limited: "Περιορισμένο", error: "Σφάλμα", skipped: "Παραλειφθέν" } },
  hi: { languageLabel: "भाषा", all: "सभी", emailPlaceholder: "somebody@example.com", run_default: "सर्च शुरू करें", export_json: "JSON एक्सपोर्ट करें", export_csv: "CSV एक्सपोर्ट करें", filter_placeholder: "साइट फ़िल्टर करें…", toast_enter_email: "कृपया ईमेल दर्ज करें", status: { registered: "रजिस्टर्ड", not_registered: "रजिस्टर नहीं", info: "जानकारी", unknown: "अज्ञात", rate_limited: "सीमित", error: "त्रुटि", skipped: "छोड़ा गया" } },
  bn: { languageLabel: "ভাষা", all: "সব", emailPlaceholder: "somebody@example.com", run_default: "স্ক্যান শুরু করুন", export_json: "JSON এক্সপোর্ট", export_csv: "CSV এক্সপোর্ট", filter_placeholder: "সাইট ফিল্টার করুন…", toast_enter_email: "দয়া করে ইমেল লিখুন", status: { registered: "নিবন্ধিত", not_registered: "নিবন্ধিত নয়", info: "তথ্য", unknown: "অজানা", rate_limited: "সীমিত", error: "ত্রুটি", skipped: "এড়ানো হয়েছে" } },
};

const DEFAULT_UI_LANG = "en";

function langKeyFromCode(code) {
  if (!code) return DEFAULT_UI_LANG;
  code = code.toLowerCase();
  if (code.startsWith("zh")) return "zh";
  if (code.startsWith("en")) return "en";
  if (code.startsWith("es")) return "es";
  if (code.startsWith("fr")) return "fr";
  if (code.startsWith("de")) return "de";
  if (code.startsWith("ja")) return "ja";
  if (code.startsWith("ko")) return "ko";
  if (code.startsWith("ru")) return "ru";
  if (code.startsWith("pt")) return "pt";
  if (code.startsWith("ar")) return "ar";
  if (code.startsWith("it")) return "it";
  if (code.startsWith("nl")) return "nl";
  if (code.startsWith("sv")) return "sv";
  if (code.startsWith("no")) return "no";
  if (code.startsWith("da")) return "da";
  if (code.startsWith("fi")) return "fi";
  if (code.startsWith("pl")) return "pl";
  if (code.startsWith("cs")) return "cs";
  if (code.startsWith("hu")) return "hu";
  if (code.startsWith("tr")) return "tr";
  if (code.startsWith("he")) return "he";
  if (code.startsWith("id")) return "id";
  if (code.startsWith("vi")) return "vi";
  if (code.startsWith("th")) return "th";
  if (code.startsWith("ms")) return "ms";
  if (code.startsWith("ro")) return "ro";
  if (code.startsWith("sk")) return "sk";
  if (code.startsWith("sr")) return "sr";
  if (code.startsWith("uk")) return "uk";
  if (code.startsWith("bg")) return "bg";
  if (code.startsWith("el")) return "el";
  if (code.startsWith("hi")) return "hi";
  if (code.startsWith("bn")) return "bn";
  return DEFAULT_UI_LANG;
}


// Use English category labels as a fallback; localized labels come from TRANSLATIONS
const CATEGORY_LABEL = (TRANSLATIONS.en && TRANSLATIONS.en.categories) || {};

// Use English data labels as fallback; localized labels come from TRANSLATIONS
const DATA_LABEL = (TRANSLATIONS.en && TRANSLATIONS.en.data_labels) || {};

const el = (id) => document.getElementById(id);
const state = {
  results: [],
  activeStatuses: new Set(),
  keyword: "",
  source: null,
  email: "",
  total: 0,
  mode: "scan", // scan | ai
  scanProfile: "reliable", // reliable | full
  aiConfigured: false,
  aiMeta: null,
  acceptLanguage: null, // null uses default server headers, '*' means accept any
  aiReport: null,
};

function t(keyPath, lang) {
  const langKey = lang || state.uiLang || langKeyFromCode(document.documentElement.lang || navigator.language);
  const parts = keyPath.split(".");
  const objLang = TRANSLATIONS[langKey] || {};
  const objDef = TRANSLATIONS[DEFAULT_UI_LANG] || {};
  let val = parts.reduce((o, p) => (o && o[p] !== undefined ? o[p] : undefined), objLang);
  if (val !== undefined) return val;
  val = parts.reduce((o, p) => (o && o[p] !== undefined ? o[p] : undefined), objDef);
  return val ?? "";
}

function applyTranslations() {
  const brandSubNode = document.querySelector(".brand-sub");
  if (brandSubNode) brandSubNode.textContent = t("brandSub");
  const apiLink = document.querySelector(".pill-link");
  if (apiLink) apiLink.textContent = t("apiDocs");
  // mode chips
  document.querySelectorAll(".mode-chip").forEach((chip) => {
    if (chip.dataset.mode === "scan" && chip.dataset.profile === "reliable") chip.textContent = t("mode_reliable");
    if (chip.dataset.mode === "scan" && chip.dataset.profile === "full") chip.textContent = t("mode_full");
    if (chip.dataset.mode === "ai") chip.textContent = t("mode_ai");
  });
  // hints and placeholders
  const modeStatus = el("mode-status");
  if (modeStatus) modeStatus.textContent = state.mode === "ai" ? (t("hint_ai_ready") || t("hint_reliable")) : (state.scanProfile === "full" ? t("hint_full") : t("hint_reliable"));
  const emailInput = el("email");
  if (emailInput) emailInput.placeholder = t("emailPlaceholder") || emailInput.placeholder;
  const keyword = el("keyword");
  if (keyword) keyword.placeholder = t("filter_placeholder") || keyword.placeholder;
  const runBtn = el("run");
  if (runBtn) runBtn.querySelector(".btn-label").textContent = state.mode === "ai" ? t("run_ai") : (state.scanProfile === "full" ? t("run_full") : t("run_default"));
  const stopBtn = el("stop");
  if (stopBtn) stopBtn.textContent = t("stop") || stopBtn.textContent;
  const progressText = el("progress-text");
  if (progressText) progressText.textContent = t("progress_connecting") || progressText.textContent;
  const exportJsonBtn = el("export-json");
  const exportCsvBtn = el("export-csv");
  if (exportJsonBtn) exportJsonBtn.textContent = t("export_json") || exportJsonBtn.textContent;
  if (exportCsvBtn) exportCsvBtn.textContent = t("export_csv") || exportCsvBtn.textContent;
  const aiTitle = document.querySelector("#ai-report-panel h3");
  if (aiTitle) aiTitle.textContent = t("ai_report_title") || aiTitle.textContent;
  const aiCols = document.querySelectorAll("#ai-report-panel h4");
  const aiH4Keys = ["ai_confirmed", "ai_intel", "ai_not_registered", "ai_likely"];
  aiCols.forEach((h4, i) => { h4.textContent = t(aiH4Keys[i]) || h4.textContent; });
  const empty = el("empty");
  if (empty) empty.textContent = t("no_results") || empty.textContent;
  // notices
  const noticeTitle = el("notice-title");
  if (noticeTitle) noticeTitle.textContent = t("notice_title") || noticeTitle.textContent;
  for (let i = 1; i <= 4; i++) {
    const n = el(`notice-${i}`);
    if (n) n.innerHTML = t(`notice_li_${i}`) || n.innerHTML;
  }
  // set document language and direction
  if (state.uiLang) {
    document.documentElement.lang = state.uiLang;
    document.documentElement.dir = state.uiLang === "ar" ? "rtl" : "ltr";
  }
  // document title
  document.title = t("title") || document.title;
}

/* ---------------- 初始化 ---------------- */
async function init() {
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
  // Language picker
  const btnLang = el("btn-lang");
  const langMenu = el("lang-menu");
  if (btnLang && langMenu) {
    const pageLang = (document.documentElement.lang || navigator.language || "en").toLowerCase();
    // initialize UI language from localStorage or page navigator
    state.uiLang = localStorage.getItem("seek_ui_lang") || langKeyFromCode(pageLang);

    const languages = [
      { value: "*", name: { zh: "所有", en: "All" } },
      { value: "zh-CN", name: { zh: "中文（简体）", en: "Chinese (Simplified)" } },
      { value: "zh", name: { zh: "中文", en: "Chinese" } },
      { value: "en", name: { zh: "英语", en: "English" } },
      { value: "en-US", name: { zh: "美国英语", en: "English (US)" } },
      { value: "fr", name: { zh: "法语", en: "French" } },
      { value: "de", name: { zh: "德语", en: "German" } },
      { value: "es", name: { zh: "西班牙语", en: "Spanish" } },
      { value: "ja", name: { zh: "日语", en: "Japanese" } },
      { value: "ko", name: { zh: "韩语", en: "Korean" } },
      { value: "ru", name: { zh: "俄语", en: "Russian" } },
      { value: "pt", name: { zh: "葡萄牙语", en: "Portuguese" } },
      { value: "ar", name: { zh: "阿拉伯语", en: "Arabic" } },
    ];

    function closeMenu() {
      langMenu.hidden = true;
      btnLang.setAttribute("aria-expanded", "false");
    }

    function openMenu() {
      langMenu.hidden = false;
      btnLang.setAttribute("aria-expanded", "true");
    }

    // populate menu (display English labels first)
    langMenu.innerHTML = "";
    languages.forEach((item) => {
      const li = document.createElement("li");
      const displayName = item.name.en || item.name[state.uiLang] || item.value;
      li.textContent = `${displayName} - ${item.value}`;
      li.dataset.value = item.value;
      li.addEventListener("click", (e) => {
        e.stopPropagation();
        const v = li.dataset.value;
        state.acceptLanguage = v === "" ? null : v;
        // update UI language when a language code is selected (not the wildcard)
        if (v && v !== "*") {
          state.uiLang = langKeyFromCode(v);
          localStorage.setItem("seek_ui_lang", state.uiLang);
          // set document language and direction
          document.documentElement.lang = v;
          document.documentElement.dir = state.uiLang === "ar" ? "rtl" : "ltr";
          applyTranslations();
          // re-render dynamic UI so translated labels update
          try {
            render();
            renderStats();
            if (state.aiReport) renderAiReport(state.aiReport);
          } catch (err) {
            console.debug('re-render after language change failed', err);
          }
        }
        btnLang.classList.toggle("pill-secondary", !!state.acceptLanguage);
        const display = (item.name.en || item.name[state.uiLang]) + (v ? `: ${v}` : "");
        btnLang.textContent = `${t("languageLabel")}: ${display}`;
        closeMenu();
      });
      langMenu.appendChild(li);
    });

    // initial button text (English display)
    const currentDisplay = languages[0].name.en || languages[0].name[state.uiLang];
    btnLang.textContent = `${t("languageLabel")}: ${currentDisplay}`;

    btnLang.addEventListener("click", (e) => {
      e.stopPropagation();
      if (langMenu.hidden) openMenu(); else closeMenu();
    });

    document.addEventListener("click", () => {
      if (!langMenu.hidden) closeMenu();
    });
  }
  // apply initial translations
  applyTranslations();
  document.querySelectorAll(".mode-chip").forEach((chip) => {
    chip.addEventListener("click", () => setMode(chip.dataset.mode, chip.dataset.profile));
  });

  try {
    const meta = await fetch("/api/meta").then((r) => r.json());
    applyMeta(meta);
  } catch (err) {
    toast(t("toast_connect_error") + err.message, true);
  }
}

function safeStart() {
  try {
    start();
  } catch (err) {
    console.error("start failed", err);
    toast(`${t("toast_start_failed")}${err.message || err}`, true);
    setRunning(false);
  }
}

function setMode(mode, profile = null) {
  if (mode === "ai" && !state.aiConfigured) {
    toast(t("toast_config_ai"), true);
    return;
  }
  state.mode = mode;
  if (mode === "scan" && profile) state.scanProfile = profile;
  document.querySelectorAll(".mode-chip").forEach((c) => {
    const selected = c.dataset.mode === mode &&
      (mode === "ai" || c.dataset.profile === state.scanProfile);
    c.classList.toggle("on", selected);
  });
  el("run").querySelector(".btn-label").textContent = mode === "ai" ? t("run_ai") : (state.scanProfile === "full" ? t("run_full") : t("run_default"));
  updateModeHint();
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
  if (!hint) return;
  if (state.mode === "ai") {
    const meta = state.aiMeta || {};
    const profileLabel = meta.profile === "full" ? t("profile_full") : t("profile_reliable");
    hint.textContent = `${t("mode_ai") || "AI"} · ${meta.model || ""} · ${profileLabel}`;
    return;
  }
  hint.textContent = state.scanProfile === "full" ? t("hint_full") : t("hint_reliable");
}

/* ---------------- 扫描 ---------------- */
function start() {
  if (state.source) return;

  const email = el("email").value.trim();
  if (!email) {
    toast(t("toast_enter_email"), true);
    el("email").focus();
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
  el("progress-text").textContent = t("progress_connecting") || "正在建立连接…";
  el("progress-count").textContent = "0 / 0";
  setRunning(true);

  if (state.mode === "ai") {
    startAi(email);
    return;
  }

  const params = new URLSearchParams({
    email,
    consent: "true",
    profile: state.scanProfile,
  });
  if (state.acceptLanguage) params.set("accept_language", state.acceptLanguage);
  const source = new EventSource(`/api/scan/stream?${params.toString()}`);
  state.source = source;

  source.addEventListener("start", (e) => {
    const data = JSON.parse(e.data);
    state.total = data.total;
    const profileLabel = (data.profile || state.scanProfile) === "full" ? t("profile_full") : t("profile_reliable");
    el("progress-text").textContent = `${profileLabel} · ${t("ai_aggregating") || "Detecting"} ${data.email}`;
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
    el("progress-text").textContent = `${t("scan_complete")} · ${((summary.elapsed_ms / 1000).toFixed(1))}s`;
    el("progress-bar").style.width = "100%";
    stop();
    renderStats(summary);
  });

  source.addEventListener("error", (e) => {
    if (e.data) {
      try {
        toast(JSON.parse(e.data).message, true);
      } catch {
        toast(t("toast_server_error"), true);
      }
    } else if (!state.results.length) {
      toast(t("toast_connection_interrupted"), true);
      el("progress-text").textContent = t("status_interrupted") || "Interrupted";
    }
    stop();
  });
}

function startAi(email) {
  const params = new URLSearchParams({ email, consent: "true" });
  if (state.acceptLanguage) params.set("accept_language", state.acceptLanguage);
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
    const profileLabel = d.profile === "full" ? t("profile_full") : t("profile_reliable");
    el("progress-text").textContent = `${profileLabel} · ${t("ai_aggregating")} · ${d.model}`;
    el("progress-count").textContent = "…";
    appendLog(`${t("ai_model")} ${d.model} @ ${d.base_url}`);
    appendLog(`${t("ai_profile")}: ${profileLabel}（SEEK_AI_PROFILE=${d.profile || "reliable"}）`);
  });

  source.addEventListener("aggregate_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = t("running_tools") || "Running tools…";
    appendLog(`${t("ai_backends_started")} : ${(d.backends || []).join(", ")}`);
  });

  source.addEventListener("backend_start", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `${t("ai_backend_running")} · ${d.name}`;
    appendLog(`▶ ${d.name} (${d.modules || "?"} modules)`);
  });

  source.addEventListener("backend_done", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`✓ ${d.name} ${t("ai_backend_done")} ${JSON.stringify(d).slice(0, 120)}`);
  });

  source.addEventListener("backend_skip", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`○ ${t("ai_backend_skipped")} ${d.name}: ${d.reason || ""}`);
  });

  source.addEventListener("aggregate_done", (e) => {
    const d = JSON.parse(e.data);
    const s = d.stats || {};
    el("progress-bar").style.width = "55%";
    el("progress-text").textContent = `${t("scan_complete")} · ${t("ai_aggregating")} · ${t("profile_reliable")}`;
    appendLog(`${t("ai_aggregate_summary")} : ${t("stats_effective")} ${s.effective ?? "?"} / ${t("status.registered")} ${s.registered ?? 0} / ${t("status.not_registered")} ${s.not_registered ?? 0} / ${t("status.info")} ${s.intel ?? 0}`);
  });

  source.addEventListener("ai_thinking", (e) => {
    const d = JSON.parse(e.data);
    el("progress-text").textContent = `${t("ai_thinking")} · ${d.round}/${d.max}`;
    el("progress-bar").style.width = `${Math.min(95, 55 + d.round * 8)}%`;
    appendLog(`${t("ai_round_label")} ${d.round}`);
  });

  source.addEventListener("ai_tool", (e) => {
    const d = JSON.parse(e.data);
    appendLog(`${t("ai_tool_calling")} ${d.name}`);
    el("progress-text").textContent = `${t("ai_tool_running")} · ${d.name}`;
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
    el("progress-text").textContent = t("ai_done") || "AI investigation complete";
    el("progress-bar").style.width = "100%";
    stop();
  });

  source.addEventListener("error", (e) => {
    if (e.data) {
      try {
        toast(JSON.parse(e.data).message, true);
      } catch {
        toast(t("ai_error"), true);
      }
    } else if (!state.results.length) {
      toast(t("ai_connection_interrupted"), true);
    }
    el("progress-text").textContent = t("status_interrupted") || "Interrupted";
    stop();
  });
}

function renderAiReport(report) {
  // cache report for re-render when language changes
  state.aiReport = report;
  el("ai-report-panel").hidden = false;
  el("ai-summary").textContent = report.summary || "";

  const stats = report.stats || {};
  const statsBox = el("ai-stats");
  const cells = [
    ["effective", t("scan_complete") || "Effective", "ok"],
    ["registered", t("status.registered") || "Registered", ""],
    ["not_registered", t("status.not_registered") || "Not registered", ""],
    ["intel", t("status.info") || "Intel", ""],
    ["failed", t("status.error") || "Failed/Unknown", "warn"],
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
        a.textContent = ` ${t("open") || "Open"}`;
        a.style.color = "var(--accent)";
        li.appendChild(a);
      }
      box.appendChild(li);
    });
    if (!(items || []).length) {
      box.innerHTML = `<li><small>${t("none") || "None"}</small></li>`;
    }
  };
  fill("ai-confirmed", report.confirmed);
  fill("ai-intel", report.intel);
  fill("ai-not-registered", report.not_registered);
  fill("ai-likely", report.likely);
  const next = el("ai-next");
  if (report.next_steps && report.next_steps.length) {
    next.innerHTML = `<strong>${t("next_steps_title")}</strong><ol>${report.next_steps
      .map((s) => `<li>${escapeHtml(s)}</li>`)
      .join("")}</ol>`;
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
  const idle = state.mode === "ai" ? t("run_ai") : (state.scanProfile === "full" ? t("run_full") : t("run_default"));
  el("run").querySelector(".btn-label").textContent = running ? t("in_progress") : idle;
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
    .filter((r) => !state.keyword || `${r.title} ${r.provider}`.toLowerCase().includes(state.keyword))
    .sort(
      (a, b) =>
        categoryRank(a.category) - categoryRank(b.category) ||
        (t(`categories.${a.category}`) || CATEGORY_LABEL[a.category] || a.category).localeCompare(
          t(`categories.${b.category}`) || CATEGORY_LABEL[b.category] || b.category,
          document.documentElement.lang || "en"
        ) ||
        STATUS_ORDER.indexOf(a.status) - STATUS_ORDER.indexOf(b.status) ||
        a.title.localeCompare(b.title, document.documentElement.lang || "en")
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
    label.textContent = t(`categories.${category}`) || CATEGORY_LABEL[category] || category;
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
  badge.textContent = t(`status.${r.status}`) || r.status;
  row.appendChild(badge);

  const avatarUrl = safeHttpUrl(r.data && r.data.avatar_url);
  if (avatarUrl) {
    const avatarLink = document.createElement("a");
    avatarLink.className = "row-avatar-link";
    avatarLink.href = avatarUrl;
    avatarLink.target = "_blank";
    avatarLink.rel = "noreferrer noopener";
    avatarLink.title = t("view_public_avatar") || "View public avatar";
      const avatar = document.createElement("img");
    avatar.className = "row-avatar";
    avatar.src = avatarUrl;
    avatar.alt = `${r.title} ${t("public_avatar") || "公开头像"}`;
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
  tag.textContent = t(`categories.${r.category}`) || CATEGORY_LABEL[r.category] || r.category;
  title.appendChild(tag);
  main.appendChild(title);

  if (r.detail) {
    const detail = document.createElement("div");
    detail.className = "row-detail";
    detail.textContent = r.detail;
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
      key.textContent = (t(`data_labels.${k}`) || DATA_LABEL[k] || k) + ":";
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
    chip.textContent = `${t(`status.${status}`) || status} ${counts[status]}`;
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
    { key: "registered", cls: "is-registered" },
    { key: "info", cls: "is-info" },
    { key: "unknown", cls: "is-unknown" },
    { key: "not_registered", cls: "" },
    { key: "error", cls: "is-error", extra: "rate_limited" },
  ];
  const box = el("stats");
  box.innerHTML = "";
  tiles.forEach((tile) => {
    const value = (counts[tile.key] || 0) + (tile.extra ? counts[tile.extra] || 0 : 0);
    const node = document.createElement("div");
    node.className = `stat ${tile.cls}`;
    const label = t(`status.${tile.key}`) || tile.key;
    node.innerHTML = `<div class="stat-value">${value}</div><div class="stat-label">${label}</div>`;
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
  if (!state.results.length) return toast(t("no_results_export"), true);
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
  if (!state.results.length) return toast(t("no_results_export"), true);
  const header = [
    t("csv_header_site") || "Site",
    t("csv_header_id") || "Identifier",
    t("csv_header_category") || "Category",
    t("csv_header_status") || "Status",
    t("csv_header_detail") || "Detail",
    t("csv_header_http") || "HTTP",
    t("csv_header_elapsed") || "Elapsed(ms)",
    t("csv_header_data") || "Extra Data",
  ];
  const escape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = [header.map(escape).join(",")];
  state.results.forEach((r) => {
    lines.push(
      [
        r.title,
        r.provider,
        CATEGORY_LABEL[r.category] || r.category,
        t(`status.${r.status}`) || r.status,
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
