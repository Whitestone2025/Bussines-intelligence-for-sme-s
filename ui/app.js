const state = {
  caseData: null,
  activeCompanyId: "",
  activeMode: localStorage.getItem("codex-briefing-mode") || "executive",
  activeSection: localStorage.getItem("codex-briefing-section") || "cover",
  activeDeliverableId: "",
};

const MODE_SECTIONS = {
  executive: [
    {id: "cover", label: "Portada"},
    {id: "thesis", label: "Tesis"},
    {id: "customer", label: "Cliente"},
    {id: "market", label: "Mercado"},
    {id: "competition", label: "Competencia"},
    {id: "viability", label: "Viabilidad"},
    {id: "decision", label: "Decision"},
    {id: "plan", label: "Plan"},
    {id: "documents", label: "Documentos"},
  ],
  audit: [{id: "audit", label: "Auditoria"}],
};

const companySelect = document.getElementById("company-select");
const websiteLink = document.getElementById("website-link");
const refreshButton = document.getElementById("refresh-button");
const projectEyebrow = document.getElementById("project-eyebrow");
const projectTitle = document.getElementById("project-title");
const heroKicker = document.getElementById("hero-kicker");
const heroTitle = document.getElementById("hero-title");
const heroSummary = document.getElementById("hero-summary");
const heroNarrative = document.getElementById("hero-narrative");
const heroBadges = document.getElementById("hero-badges");
const companyMeta = document.getElementById("company-meta");
const modeSwitch = document.getElementById("mode-switch");
const sectionNav = document.getElementById("section-nav");
const statusBanner = document.getElementById("status-banner");
const chapterIntro = document.getElementById("chapter-intro");
const chapterMetrics = document.getElementById("chapter-metrics");
const sectionContent = document.getElementById("section-content");
const heroTitleLabel = document.getElementById("hero-title-label");

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json();
}

function setStatus(message, tone = "neutral") {
  statusBanner.textContent = message;
  statusBanner.dataset.tone = tone;
}

function formatMoney(value, currencyCode = "MXN") {
  if (value === undefined || value === null || value === "") return "Sin dato";
  try {
    return new Intl.NumberFormat("es-MX", {
      style: "currency",
      currency: currencyCode,
      maximumFractionDigits: 0,
    }).format(Number(value));
  } catch {
    return `${currencyCode} ${value}`;
  }
}

function formatNumber(value, digits = 0) {
  if (value === undefined || value === null || value === "") return "Sin dato";
  return new Intl.NumberFormat("es-MX", {maximumFractionDigits: digits}).format(Number(value));
}

function toneForStatus(status) {
  if (!status) return "neutral";
  if (["ready", "validated", "confirmed"].includes(status)) return "good";
  if (["needs_validation", "partially_ready", "inferred"].includes(status)) return "warn";
  return "neutral";
}

function humanStatus(status) {
  const mapping = {
    draft: "borrador",
    inferred: "inferido",
    needs_validation: "por validar",
    validated: "validado",
    confirmed: "confirmado",
    ready: "listo",
    partially_ready: "parcial",
    stale: "desactualizado",
    open: "abierto",
  };
  return mapping[status] || status || "sin estado";
}

function competitorTypeLabel(value) {
  const mapping = {
    direct: "competidor directo",
    substitute: "sustituto",
  };
  return mapping[value] || value || "competidor";
}

function currentSummary() {
  return state.caseData?.summary || {};
}

function chapterById(id) {
  return (MODE_SECTIONS[state.activeMode] || []).find((item) => item.id === id);
}

function hasActiveCase() {
  return Boolean(state.caseData?.company?.company_id);
}

function ensureValidState() {
  if (!MODE_SECTIONS[state.activeMode]) state.activeMode = "executive";
  const validSections = MODE_SECTIONS[state.activeMode].map((item) => item.id);
  if (!validSections.includes(state.activeSection)) {
    state.activeSection = validSections[0];
  }
  localStorage.setItem("codex-briefing-mode", state.activeMode);
  localStorage.setItem("codex-briefing-section", state.activeSection);
}

function badge(label, tone = "neutral") {
  return `<span class="status-chip status-chip-${tone}">${escapeHtml(label)}</span>`;
}

function listMarkup(items, empty = "Sin informacion disponible.") {
  if (!items || !items.length) return `<p class="empty-state">${escapeHtml(empty)}</p>`;
  return `<ul class="plain-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function markdownToHtml(content) {
  if (!content) return "<p class='empty-state'>Sin contenido.</p>";
  const lines = content.split("\n");
  const parts = [];
  let listBuffer = [];

  const flushList = () => {
    if (!listBuffer.length) return;
    parts.push(`<ul class="doc-list">${listBuffer.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`);
    listBuffer = [];
  };

  lines.forEach((rawLine) => {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      return;
    }
    if (line.startsWith("### ")) {
      flushList();
      parts.push(`<h4>${escapeHtml(line.slice(4))}</h4>`);
      return;
    }
    if (line.startsWith("## ")) {
      flushList();
      parts.push(`<h3>${escapeHtml(line.slice(3))}</h3>`);
      return;
    }
    if (line.startsWith("# ")) {
      flushList();
      parts.push(`<h2>${escapeHtml(line.slice(2))}</h2>`);
      return;
    }
    if (line.startsWith("- ")) {
      listBuffer.push(line.slice(2));
      return;
    }
    flushList();
    parts.push(`<p>${escapeHtml(line)}</p>`);
  });

  flushList();
  return parts.join("");
}

function chapterPill(section, count) {
  return `
    <button class="index-link ${section.id === state.activeSection ? "active" : ""}" data-section="${section.id}" type="button">
      <span>${escapeHtml(section.label)}</span>
      ${count ? `<small>${escapeHtml(String(count))}</small>` : ""}
    </button>
  `;
}

function sectionCount(sectionId) {
  const payload = state.caseData || {};
  if (sectionId === "documents") return (payload.deliverable_index || []).length || "";
  if (sectionId === "audit") {
    const counts = payload.audit_index?.counts || {};
    return (counts.sources || 0) + (counts.evidence || 0) + (counts.findings || 0) || "";
  }
  const block = {
    thesis: payload.thesis?.highlights?.length,
    customer: payload.thesis?.buyer_truths?.pains?.length,
    market: payload.market_summary?.records?.length,
    competition: payload.competition_summary?.competitors?.length,
    viability: payload.viability_summary?.flags?.length,
    decision: payload.decision_summary?.memo?.next_steps?.length,
    plan: payload.decision_summary?.milestones?.length,
  }[sectionId];
  return block || "";
}

function renderCompanySelect() {
  const companies = state.caseData?.companies || [];
  companySelect.innerHTML = companies
    .map((company) => `<option value="${escapeHtml(company.company_id)}">${escapeHtml(company.name)}</option>`)
    .join("");
  if (state.activeCompanyId) companySelect.value = state.activeCompanyId;
}

function renderProjectBranding() {
  const project = state.caseData?.project || {};
  const name = project.name || "Ws B-I";
  const tagline = project.tagline || "Business intelligence operativo para decisiones en Mexico.";
  document.title = name;
  projectEyebrow.textContent = name;
  projectTitle.textContent = tagline;
}

function renderModeSwitch() {
  modeSwitch.innerHTML = [
    {id: "executive", label: "Briefing"},
    {id: "audit", label: "Auditoria"},
  ]
    .map(
      (mode) => `
        <button class="mode-pill ${mode.id === state.activeMode ? "active" : ""}" data-mode="${mode.id}" type="button">
          ${escapeHtml(mode.label)}
        </button>
      `
    )
    .join("");

  modeSwitch.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeMode = button.dataset.mode || "executive";
      state.activeSection = state.activeMode === "audit" ? "audit" : "cover";
      ensureValidState();
      renderApp();
      window.scrollTo({top: 0, behavior: "smooth"});
    });
  });
}

function renderSectionNav() {
  if (!hasActiveCase()) {
    sectionNav.innerHTML = "";
    return;
  }
  const sections = MODE_SECTIONS[state.activeMode] || [];
  sectionNav.innerHTML = sections.map((section) => chapterPill(section, sectionCount(section.id))).join("");
  sectionNav.querySelectorAll("[data-section]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.section || "cover";
      state.activeSection = target;
      ensureValidState();
      renderSectionNav();
      const node = document.getElementById(`chapter-${target}`);
      if (node) node.scrollIntoView({behavior: "smooth", block: "start"});
    });
  });
}

function renderHero() {
  if (!hasActiveCase()) {
    const onboarding = state.caseData?.onboarding || {};
    heroKicker.textContent = "Inicio guiado";
    heroTitleLabel.textContent = "Workspace";
    heroTitle.textContent = "Ws B-I";
    heroSummary.textContent = onboarding.headline || "Workspace listo para iniciar.";
    heroNarrative.textContent = onboarding.summary || "Pidele a Codex que cargue tu negocio y te guie paso a paso.";
    heroBadges.innerHTML = [badge("sin caso activo", "warn"), badge("guiado por Codex", "neutral")].join("");
    companyMeta.innerHTML = `
      <div class="meta-line"><span>Siguiente paso</span><strong>Pedirle a Codex que inicie tu caso</strong></div>
      <div class="meta-line"><span>Modo recomendado</span><strong>Guiado para no tecnicos</strong></div>
      <div class="meta-line"><span>Objetivo</span><strong>Ver tu negocio en el frontend</strong></div>
      <div class="meta-line"><span>Estado</span><strong>Listo para empezar</strong></div>
    `;
    websiteLink.classList.add("hidden");
    return;
  }
  const hero = state.caseData?.hero || {};
  const summary = currentSummary();
  const warRoom = state.caseData?.war_room || {};

  heroKicker.textContent = state.activeMode === "audit" ? "Modo auditoria" : "Modo briefing";
  heroTitleLabel.textContent = state.activeMode === "audit" ? "Apéndice y trazabilidad" : "Caso activo";
  heroTitle.textContent = hero.title || "Caso activo";
  heroSummary.textContent = hero.subtitle || "Sin titular ejecutivo.";
  heroNarrative.textContent = hero.narrative || hero.summary || "Sin narrativa disponible.";
  heroBadges.innerHTML = [
    ...(hero.badges || []).map((item) => badge(item.label, item.tone || "neutral")),
    hero.status ? badge(humanStatus(hero.status), toneForStatus(hero.status)) : "",
  ].join("");

  companyMeta.innerHTML = `
    <div class="meta-line"><span>Industria</span><strong>${escapeHtml(summary.industry || "Sin industria")}</strong></div>
    <div class="meta-line"><span>Region</span><strong>${escapeHtml(summary.region || "Mexico")}</strong></div>
    <div class="meta-line"><span>Canal</span><strong>${escapeHtml(summary.channel?.name || "Sin canal")}</strong></div>
    <div class="meta-line"><span>Tesis actual</span><strong>${escapeHtml(warRoom.recommendation || "Sin decision")}</strong></div>
  `;

  if (hero.website) {
    websiteLink.href = hero.website;
    websiteLink.classList.remove("hidden");
  } else {
    websiteLink.classList.add("hidden");
  }
}

function metricBlock(label, value) {
  return `
    <article class="metric-block">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </article>
  `;
}

function renderChapterIntro() {
  if (!hasActiveCase()) {
    chapterIntro.innerHTML = `
      <section class="memo-strip">
        <p class="eyebrow">Primer paso</p>
        <h3>Empieza hablando con Codex, no con la terminal</h3>
        <p>Ws B-I esta preparado para que un duenio de PyME pueda arrancar sin ser tecnico. Codex debe hacer el trabajo operativo por ti.</p>
      </section>
    `;
    return;
  }
  if (state.activeMode === "audit") {
    const audit = state.caseData?.audit_index || {};
    chapterIntro.innerHTML = `
      <section class="memo-strip">
        <p class="eyebrow">Apéndice</p>
        <h3>${escapeHtml(audit.headline || "Auditoria del caso")}</h3>
        <p>${escapeHtml(audit.summary || "Inspeccion de trazabilidad y evidencia.")}</p>
      </section>
    `;
    return;
  }

  const summary = currentSummary();
  const warRoom = state.caseData?.war_room || {};
  chapterIntro.innerHTML = `
    <section class="memo-strip">
      <p class="eyebrow">Resumen ejecutivo</p>
      <h3>${escapeHtml(warRoom.recommendation || "Sin recomendacion central")}</h3>
      <p>${escapeHtml(warRoom.rationale || summary.seed_summary || "Sin resumen ejecutivo.")}</p>
    </section>
  `;
}

function renderChapterMetrics() {
  if (!hasActiveCase()) {
    chapterMetrics.innerHTML = [
      metricBlock("Estado", "Workspace vacio"),
      metricBlock("Siguiente paso", "Pidele a Codex que inicie tu caso"),
      metricBlock("Meta", "Ver tu negocio en el frontend"),
    ].join("");
    return;
  }
  const payload = state.caseData || {};
  const summary = payload.summary || {};
  const readiness = summary.readiness || {};
  const pricing = payload.viability_summary?.pricing || {};
  const financials = payload.viability_summary?.financials || {};
  const counts = payload.audit_index?.counts || {};

  chapterMetrics.innerHTML = [
    metricBlock("Preparacion", `${humanStatus(readiness.status || "draft")} · ${formatNumber(readiness.score || 0)}`),
    metricBlock("Fuentes", formatNumber(counts.sources || summary.source_count || 0)),
    metricBlock("Evidencias", formatNumber(counts.evidence || summary.evidence_count || 0)),
    metricBlock("Precio objetivo", formatMoney(pricing.price_target, pricing.currency_code || "MXN")),
    metricBlock("LTV:CAC", formatNumber(financials.ltv_cac_ratio || 0, 2)),
    metricBlock("Entregables", formatNumber((payload.deliverable_index || []).length)),
  ].join("");
}

function spread(title, summary, left, right = "") {
  return `
    <section class="report-spread">
      <header class="spread-head">
        <h4>${escapeHtml(title)}</h4>
        <p>${escapeHtml(summary)}</p>
      </header>
      <div class="spread-body ${right ? "two-column" : ""}">
        <div class="spread-column">${left}</div>
        ${right ? `<div class="spread-column spread-side">${right}</div>` : ""}
      </div>
    </section>
  `;
}

function sheet(title, body, eyebrow = "") {
  return `
    <article class="sheet">
      ${eyebrow ? `<p class="eyebrow">${escapeHtml(eyebrow)}</p>` : ""}
      <h5>${escapeHtml(title)}</h5>
      ${body}
    </article>
  `;
}

function chapterWrapper(id, label, title, summary, body) {
  return `
    <section id="chapter-${escapeHtml(id)}" class="report-chapter">
      <div class="chapter-banner">
        <p class="eyebrow">${escapeHtml(label)}</p>
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(summary)}</p>
      </div>
      ${body}
    </section>
  `;
}

function renderCoverChapter() {
  const warRoom = state.caseData?.war_room || {};
  const summary = currentSummary();
  const snapshot = warRoom.commercial_snapshot || {};
  const deliverables = warRoom.featured_deliverables || [];

  const left = `
    ${sheet(
      "La jugada que recomendamos",
      `
        <p class="big-statement">${escapeHtml(warRoom.recommendation || "Sin recomendacion.")}</p>
        <p>${escapeHtml(warRoom.rationale || "Sin fundamento.")}</p>
      `,
      "Tesis central"
    )}
    ${sheet(
      "Lo que ya sabemos",
      listMarkup([
        summary.seed_summary || "",
        `Oferta actual: ${summary.offer?.name || "Sin oferta"}`,
        `Cliente central: ${summary.icp?.label || "Sin ICP"}`,
        `Canal prioritario: ${summary.channel?.name || "Sin canal"}`,
      ]),
      "Base del caso"
    )}
  `;

  const right = `
    ${sheet(
      "Marco comercial",
      `
        <dl class="definition-list">
          <div><dt>Piso</dt><dd>${escapeHtml(formatMoney(snapshot.price_floor, snapshot.currency_code || "MXN"))}</dd></div>
          <div><dt>Objetivo</dt><dd>${escapeHtml(formatMoney(snapshot.price_target, snapshot.currency_code || "MXN"))}</dd></div>
          <div><dt>Techo</dt><dd>${escapeHtml(formatMoney(snapshot.price_ceiling, snapshot.currency_code || "MXN"))}</dd></div>
        </dl>
      `,
      "Pricing"
    )}
    ${sheet("Riesgos principales", listMarkup(warRoom.risks, "Sin riesgos."), "Lo que puede romper la tesis")}
    ${sheet(
      "Documentos listos",
      deliverables
        .map(
          (item) => `
            <button class="document-line" type="button" data-open-section="documents" data-open-deliverable="${escapeHtml(item.id)}">
              <strong>${escapeHtml(item.title)}</strong>
              <span>${escapeHtml(item.summary || "Sin resumen")}</span>
            </button>
          `
        )
        .join(""),
      "Lectura lista"
    )}
  `;

  return chapterWrapper(
    "cover",
    "Portada",
    "Portada ejecutiva",
    "La lectura completa del caso en una sola superficie.",
    spread("Sintesis de direccion", "La recomendacion, el marco comercial y los riesgos del caso.", left, right)
  );
}

function renderThesisChapter() {
  const thesis = state.caseData?.thesis || {};
  const offer = thesis.offer || {};
  const messaging = thesis.messaging || {};

  return chapterWrapper(
    "thesis",
    "Tesis",
    thesis.headline || "Tesis del negocio",
    thesis.summary || "Servicio, oferta y narrativa central.",
    spread(
      "Lo que vende realmente",
      "Definicion del servicio, propuesta de valor y narrativa visible.",
      `
        ${sheet(
          "Servicio",
          `
            <p class="big-statement">${escapeHtml(thesis.service_statement || "Sin definicion del servicio.")}</p>
            <p>${escapeHtml(offer.core_promise || thesis.summary || "Sin promesa central.")}</p>
          `,
          "Servicio"
        )}
        ${sheet("Oferta", `<p>${escapeHtml(offer.mechanism || "Sin mecanismo definido.")}</p>${listMarkup(offer.proof_points, "Sin pruebas.")}`, "Mecanismo")}
      `,
      `
        ${sheet("Headline", `<p class="big-statement">${escapeHtml(messaging.headline || "Sin headline.")}</p><p>${escapeHtml(messaging.subheadline || "Sin subheadline.")}</p>`, "Narrativa")}
        ${sheet("Pruebas comerciales", listMarkup(messaging.proof_points, "Sin pruebas."), "Sustento")}
      `
    )
  );
}

function renderCustomerChapter() {
  const thesis = state.caseData?.thesis || {};
  const truths = thesis.buyer_truths || {};
  const icp = thesis.icp || {};
  const messaging = thesis.messaging || {};

  return chapterWrapper(
    "customer",
    "Cliente",
    "Cliente y momento de compra",
    "A quien perseguir, por que compra y que frena la decision.",
    spread(
      "Comprador real",
      "Buyer truths, objeciones y guion comercial.",
      `
        ${sheet(
          "ICP",
          `
            <p class="big-statement">${escapeHtml(icp.label || "Sin ICP.")}</p>
            <div class="inline-status">
              ${badge(humanStatus(icp.status || "draft"), toneForStatus(icp.status))}
              ${badge(`confianza ${Number(icp.confidence || 0).toFixed(2)}`, "neutral")}
            </div>
          `,
          "Segmento"
        )}
        ${sheet("Dolores", listMarkup(truths.pains, "Sin dolores."), "Friccion")}
        ${sheet("Resultados que busca", listMarkup(truths.outcomes, "Sin resultados."), "Outcomes")}
      `,
      `
        ${sheet("Objeciones reales", listMarkup(truths.objections, "Sin objeciones."), "Lo que bloquea")}
        ${sheet("Pruebas de confianza", listMarkup(truths.trust_signals, "Sin senales."), "Confianza")}
        ${sheet("Como responder objeciones", listMarkup(messaging.objection_handlers, "Sin respuestas."), "Guion")}
      `
    )
  );
}

function renderMarketChapter() {
  const market = state.caseData?.market_summary || {};
  const records = market.records || [];

  return chapterWrapper(
    "market",
    "Mercado",
    market.headline || "Mercado",
    market.summary || "Tamano de oportunidad y confianza de los supuestos.",
    spread(
      "Mercado y supuestos",
      "Lectura del tamano de oportunidad, no solo numerica sino explicativa.",
      `
        <div class="market-rail">
          ${records
            .map(
              (record) => `
                <article class="market-card">
                  <span>${escapeHtml(record.label)}</span>
                  <strong>${escapeHtml(
                    record.label === "Atractivo"
                      ? formatNumber(record.value, 2)
                      : formatMoney(record.value, record.currency_code || "MXN")
                  )}</strong>
                  <p>${escapeHtml(record.segment_name || "Sin segmento")}</p>
                </article>
              `
            )
            .join("")}
        </div>
      `,
      records
        .map((record) => sheet(record.label, listMarkup(record.key_assumptions, "Sin supuestos."), "Supuestos"))
        .join("")
    )
  );
}

function renderCompetitionChapter() {
  const competition = state.caseData?.competition_summary || {};
  const competitors = competition.competitors || [];

  return chapterWrapper(
    "competition",
    "Competencia",
    competition.headline || "Competencia",
    competition.summary || "Mapa competitivo y whitespace actual.",
    spread(
      "Alternativas del cliente",
      "Tabla comparativa enfocada en lectura estrategica, no en cards aisladas.",
      `
        <table class="report-table">
          <thead>
            <tr>
              <th>Alternativa</th>
              <th>Tipo</th>
              <th>Posicionamiento</th>
              <th>Fortalezas</th>
              <th>Debilidades</th>
            </tr>
          </thead>
          <tbody>
            ${competitors
              .map(
                (item) => `
                  <tr>
                    <td><strong>${escapeHtml(item.name || "Competidor")}</strong></td>
                    <td>${escapeHtml(competitorTypeLabel(item.competitor_type))}</td>
                    <td>${escapeHtml(item.positioning_summary || "Sin posicionamiento.")}</td>
                    <td>${(item.strengths || []).map((value) => `<div>${escapeHtml(value)}</div>`).join("") || "Sin fortalezas."}</td>
                    <td>${(item.weaknesses || []).map((value) => `<div>${escapeHtml(value)}</div>`).join("") || "Sin debilidades."}</td>
                  </tr>
                `
              )
              .join("")}
          </tbody>
        </table>
      `,
      sheet("Whitespace", listMarkup(competition.whitespace, "Sin whitespace."), "Donde ganar")
    )
  );
}

function renderViabilityChapter() {
  const viability = state.caseData?.viability_summary || {};
  const pricing = viability.pricing || {};
  const financials = viability.financials || {};

  return chapterWrapper(
    "viability",
    "Viabilidad",
    viability.headline || "Pricing y viabilidad",
    viability.summary || "Lo que sostienen hoy precio, margen y supuestos.",
    spread(
      "Economia del caso",
      "Pricing y viabilidad en formato de memo operativo.",
      `
        ${sheet(
          "Escalera de precio",
          `
            <dl class="definition-list">
              <div><dt>Piso</dt><dd>${escapeHtml(formatMoney(pricing.price_floor, pricing.currency_code || "MXN"))}</dd></div>
              <div><dt>Objetivo</dt><dd>${escapeHtml(formatMoney(pricing.price_target, pricing.currency_code || "MXN"))}</dd></div>
              <div><dt>Techo</dt><dd>${escapeHtml(formatMoney(pricing.price_ceiling, pricing.currency_code || "MXN"))}</dd></div>
            </dl>
          `,
          "Precio"
        )}
        ${sheet(
          "Tiers",
          (pricing.tier_summaries || [])
            .map(
              (tier) => `
                <article class="mini-sheet">
                  <strong>${escapeHtml(tier.name || "Tier")}</strong>
                  <span>${escapeHtml(formatMoney(tier.price, pricing.currency_code || "MXN"))}</span>
                  <p>${escapeHtml(tier.value_summary || "Sin descripcion.")}</p>
                </article>
              `
            )
            .join(""),
          "Oferta comercial"
        )}
      `,
      `
        ${sheet(
          "Viabilidad",
          `
            <dl class="definition-list">
              <div><dt>LTV</dt><dd>${escapeHtml(formatMoney(financials.estimated_ltv, financials.currency_code || "MXN"))}</dd></div>
              <div><dt>CAC</dt><dd>${escapeHtml(formatMoney(financials.estimated_cac, financials.currency_code || "MXN"))}</dd></div>
              <div><dt>LTV:CAC</dt><dd>${escapeHtml(formatNumber(financials.ltv_cac_ratio, 2))}</dd></div>
              <div><dt>Payback</dt><dd>${escapeHtml(financials.payback_months ? `${formatNumber(financials.payback_months, 1)} meses` : "Sin dato")}</dd></div>
              <div><dt>Break-even</dt><dd>${escapeHtml(formatNumber(financials.break_even_customers, 1))}</dd></div>
              <div><dt>Margen</dt><dd>${escapeHtml(financials.gross_margin_ratio ? `${formatNumber(financials.gross_margin_ratio * 100, 1)}%` : "Sin dato")}</dd></div>
            </dl>
          `,
          "Finanzas"
        )}
        ${sheet("Alertas", listMarkup(viability.flags, "Sin alertas."), "Riesgo")}
      `
    )
  );
}

function renderDecisionChapter() {
  const decisionSummary = state.caseData?.decision_summary || {};
  const memo = decisionSummary.memo || {};

  return chapterWrapper(
    "decision",
    "Decision",
    decisionSummary.headline || "Decision",
    decisionSummary.summary || "La jugada y por que ahora.",
    spread(
      "Decision actual",
      "La recomendacion, sus alternativas y los riesgos asociados.",
      `
        ${sheet(
          "Recomendacion",
          `
            <p class="big-statement">${escapeHtml(memo.recommended_action || "Sin decision.")}</p>
            <p>${escapeHtml(memo.why_now || "Sin fundamento.")}</p>
          `,
          "Accion principal"
        )}
        ${sheet("Alternativas", listMarkup(memo.alternative_actions, "Sin alternativas."), "Alternativas")}
      `,
      `
        ${sheet("Riesgos", listMarkup(memo.key_risks, "Sin riesgos."), "Riesgo")}
        ${sheet("Proximos pasos", listMarkup(memo.next_steps, "Sin pasos."), "Activacion")}
      `
    )
  );
}

function renderPlanChapter() {
  const decisionSummary = state.caseData?.decision_summary || {};
  const plan = decisionSummary.plan || {};
  const milestones = decisionSummary.milestones || [];

  return chapterWrapper(
    "plan",
    "Plan",
    "Plan 30/60/90",
    "Ruta de ejecucion para convertir la decision en pruebas y activos.",
    spread(
      "Ruta operativa",
      "Plan secuencial de 30, 60 y 90 dias.",
      `
        ${sheet(
          "Objetivo del plan",
          `<p class="big-statement">${escapeHtml(plan.objective || "Sin objetivo del plan.")}</p>`,
          "Objetivo"
        )}
      `,
      `
        <div class="timeline-stack">
          ${milestones
            .map(
              (milestone) => `
                <article class="timeline-row">
                  <span>${escapeHtml(milestone.timeframe || "Hito")}</span>
                  <strong>${escapeHtml(milestone.name || "Sin nombre")}</strong>
                  <p>${escapeHtml(milestone.success_metric || "Sin metrica.")}</p>
                </article>
              `
            )
            .join("")}
        </div>
      `
    )
  );
}

function renderDocumentsChapter() {
  const deliverables = state.caseData?.deliverable_index || [];
  if (!deliverables.length) {
    return chapterWrapper("documents", "Documentos", "Documentos", "No hay documentos disponibles.", "<p class='empty-state'>Sin documentos.</p>");
  }
  if (!state.activeDeliverableId || !deliverables.some((item) => item.id === state.activeDeliverableId)) {
    state.activeDeliverableId = deliverables[0].id;
  }
  const active = deliverables.find((item) => item.id === state.activeDeliverableId) || deliverables[0];

  return chapterWrapper(
    "documents",
    "Documentos",
    "Lector de documentos",
    "Memo, diagnostico, deck y riesgos en formato de lectura editorial.",
    `
      <div class="document-layout">
        <aside class="document-index">
          ${deliverables
            .map(
              (item) => `
                <button class="document-index-item ${item.id === state.activeDeliverableId ? "active" : ""}" data-deliverable="${escapeHtml(item.id)}" type="button">
                  <strong>${escapeHtml(item.title)}</strong>
                  <span>${escapeHtml(item.summary || "Sin resumen")}</span>
                </button>
              `
            )
            .join("")}
        </aside>
        <article class="document-page">
          <header class="document-page-head">
            <p class="eyebrow">Documento activo</p>
            <h4>${escapeHtml(active.title)}</h4>
            <p>${escapeHtml(active.summary || "Sin resumen")}</p>
          </header>
          <div class="document-body">${markdownToHtml(active.content || "")}</div>
        </article>
      </div>
    `
  );
}

function renderWelcomeChapter() {
  const onboarding = state.caseData?.onboarding || {};
  const starterPrompt = onboarding.starter_prompt || "Corre Ws B-I para mi negocio y guiame paso a paso hasta que pueda ver mi informacion en el frontend.";
  const steps = onboarding.steps || [];
  return `
    <section id="chapter-welcome" class="report-chapter">
      <div class="chapter-banner">
        <p class="eyebrow">Inicio</p>
        <h3>${escapeHtml(onboarding.headline || "Workspace listo para iniciar")}</h3>
        <p>${escapeHtml(onboarding.summary || "Pidele a Codex que inicie tu caso de negocio.")}</p>
      </div>
      <section class="report-spread">
        <header class="spread-head">
          <h4>Como empezar</h4>
          <p>La forma correcta de usar Ws B-I como usuario no tecnico es pedirle a Codex que lo corra por ti.</p>
        </header>
        <div class="spread-body two-column">
          <div class="spread-column">
            ${sheet(
              "Mensaje recomendado",
              `<p class="big-statement">${escapeHtml(starterPrompt)}</p>`,
              "Habla con Codex"
            )}
            ${sheet(
              "Que debes compartir",
              listMarkup([
                "Nombre de tu negocio",
                "Que vendes en una o dos frases",
                "Ciudad o region",
                "Chats, notas, links, PDFs o material real",
              ]),
              "Informacion minima"
            )}
          </div>
          <div class="spread-column spread-side">
            ${sheet("Que hara Codex", listMarkup(steps, "Sin pasos."), "Proceso guiado")}
          </div>
        </div>
      </section>
    </section>
  `;
}

function renderAuditPage() {
  const audit = state.caseData?.audit_index || {};
  const counts = audit.counts || {};
  const traceability = audit.traceability || {};
  return `
    <section id="chapter-audit" class="report-chapter report-chapter-audit">
      <div class="chapter-banner">
        <p class="eyebrow">Auditoria</p>
        <h3>${escapeHtml(audit.headline || "Auditoria del caso")}</h3>
        <p>${escapeHtml(audit.summary || "Inspeccion de trazabilidad y evidencia.")}</p>
      </div>
      <div class="audit-ledger">
        ${sheet(
          "Contadores del caso",
          `
            <dl class="definition-list">
              <div><dt>Fuentes</dt><dd>${escapeHtml(formatNumber(counts.sources || 0))}</dd></div>
              <div><dt>Evidencias</dt><dd>${escapeHtml(formatNumber(counts.evidence || 0))}</dd></div>
              <div><dt>Findings</dt><dd>${escapeHtml(formatNumber(counts.findings || 0))}</dd></div>
              <div><dt>Validacion</dt><dd>${escapeHtml(formatNumber(counts.validation || 0))}</dd></div>
            </dl>
          `,
          "Resumen"
        )}
        ${sheet(
          "Trazabilidad",
          `
            <div class="trace-columns">
              <div><h5>Decision</h5>${listMarkup((traceability.decision || []).map((item) => item.title), "Sin refs.")}</div>
              <div><h5>Oferta</h5>${listMarkup((traceability.offer || []).map((item) => item.title), "Sin refs.")}</div>
              <div><h5>Pricing</h5>${listMarkup((traceability.pricing || []).map((item) => item.title), "Sin refs.")}</div>
              <div><h5>Mercado</h5>${listMarkup((traceability.market || []).map((item) => item.title), "Sin refs.")}</div>
            </div>
          `,
          "Apéndice"
        )}
        ${sheet(
          "Fuentes",
          (audit.sources || [])
            .map(
              (item) => `
                <article class="ledger-item">
                  <div>
                    <span>${escapeHtml(item.source_kind || "fuente")}</span>
                    <strong>${escapeHtml(item.title || "Fuente")}</strong>
                  </div>
                  <p>${escapeHtml(item.summary || "Sin resumen")}</p>
                </article>
              `
            )
            .join("") || "<p class='empty-state'>Sin fuentes.</p>",
          "Fuentes"
        )}
        ${sheet(
          "Evidencia",
          (audit.evidence || [])
            .slice(0, 12)
            .map(
              (item) => `
                <article class="ledger-item">
                  <div>
                    <span>${escapeHtml(item.source_type || item.channel || "evidencia")}</span>
                    <strong>${escapeHtml(item.title || item.id)}</strong>
                  </div>
                  <p>${escapeHtml(item.summary || "Sin resumen")}</p>
                </article>
              `
            )
            .join("") || "<p class='empty-state'>Sin evidencias.</p>",
          "Ledger"
        )}
      </div>
    </section>
  `;
}

function renderExecutivePage() {
  return `
    ${renderCoverChapter()}
    ${renderThesisChapter()}
    ${renderCustomerChapter()}
    ${renderMarketChapter()}
    ${renderCompetitionChapter()}
    ${renderViabilityChapter()}
    ${renderDecisionChapter()}
    ${renderPlanChapter()}
    ${renderDocumentsChapter()}
  `;
}

function attachInteractions() {
  sectionContent.querySelectorAll("[data-deliverable]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeDeliverableId = button.dataset.deliverable || "";
      renderBody();
      const node = document.getElementById("chapter-documents");
      if (node) node.scrollIntoView({behavior: "smooth", block: "start"});
    });
  });

  sectionContent.querySelectorAll("[data-open-section]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeMode = "executive";
      state.activeSection = button.dataset.openSection || "documents";
      if (button.dataset.openDeliverable) {
        state.activeDeliverableId = button.dataset.openDeliverable;
      }
      ensureValidState();
      renderApp();
      const node = document.getElementById(`chapter-${state.activeSection}`);
      if (node) node.scrollIntoView({behavior: "smooth", block: "start"});
    });
  });
}

function renderBody() {
  if (!hasActiveCase()) {
    sectionContent.innerHTML = renderWelcomeChapter();
    return;
  }
  sectionContent.innerHTML = state.activeMode === "audit" ? renderAuditPage() : renderExecutivePage();
  attachInteractions();
}

function renderApp() {
  ensureValidState();
  renderProjectBranding();
  renderCompanySelect();
  renderModeSwitch();
  renderSectionNav();
  renderHero();
  renderChapterIntro();
  renderChapterMetrics();
  renderBody();
}

function chooseInitialCompany(casePayload) {
  const remembered = localStorage.getItem("codex-active-company") || "";
  const companies = casePayload?.companies || [];
  if (remembered && companies.some((company) => company.company_id === remembered)) {
    return remembered;
  }
  return casePayload?.company?.company_id || "";
}

function handleError(error) {
  console.error(error);
  setStatus(error.message || "Ocurrio un error al cargar el caso.", "error");
  sectionContent.innerHTML = `<section class="report-chapter"><p class="empty-state">${escapeHtml(error.message || "Error desconocido.")}</p></section>`;
}

async function loadCase(companyId = "", announce = false) {
  const query = companyId ? `?company_id=${encodeURIComponent(companyId)}` : "";
  const payload = await api(`/api/case${query}`);
  state.caseData = payload;
  state.activeCompanyId = payload.company?.company_id || companyId || "";
  if (state.activeCompanyId) {
    localStorage.setItem("codex-active-company", state.activeCompanyId);
  }
  ensureValidState();
  renderApp();
  if (!payload.company?.name) {
    setStatus("Workspace listo para iniciar. Pidele a Codex que cargue tu negocio.", "neutral");
    return;
  }
  setStatus(`${announce ? "Caso actualizado" : "Caso cargado"} para ${payload.company?.name || state.activeCompanyId}.`, announce ? "success" : "neutral");
}

companySelect.addEventListener("change", () => {
  loadCase(companySelect.value, true).catch(handleError);
});

refreshButton.addEventListener("click", () => {
  loadCase(state.activeCompanyId, true).catch(handleError);
});

async function boot() {
  const payload = await api("/api/case");
  const initialCompanyId = chooseInitialCompany(payload);
  state.caseData = payload;
  state.activeCompanyId = payload.company?.company_id || "";
  if (initialCompanyId && initialCompanyId !== state.activeCompanyId) {
    await loadCase(initialCompanyId);
    return;
  }
  ensureValidState();
  renderApp();
  if (!payload.company?.name) {
    setStatus("Workspace listo para iniciar. Pidele a Codex que cargue tu negocio.", "neutral");
    return;
  }
  setStatus(`Caso cargado para ${payload.company?.name || state.activeCompanyId}.`, "neutral");
}

boot().catch(handleError);
