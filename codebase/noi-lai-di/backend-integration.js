/* Connect the VLearn prototype to the existing Adaptive Learning FastAPI API. */
(() => {
  "use strict";

  const backendFromQuery = new URLSearchParams(window.location.search).get("api");
  const defaultBackend = window.location.port === "8000"
    ? window.location.origin
    : window.location.protocol.startsWith("http")
      ? `${window.location.protocol}//${window.location.hostname}:8000`
      : "http://127.0.0.1:8000";
  const API_BASE = (
    backendFromQuery && /^https?:\/\//i.test(backendFromQuery)
      ? backendFromQuery
      : defaultBackend
  ).replace(/\/+$/, "");

  class LiveApiError extends Error {
    constructor(message, code = "BACKEND_REQUEST_FAILED", status = 0) {
      super(message);
      this.code = code;
      this.status = status;
    }
  }

  const LIVE = {
    active: false,
    file: null,
    pdfUrl: "",
    document: null,
    processing: null,
    units: [],
    activeUnit: null,
    currentPage: 1,
    sessions: new Map(),
    retry: null,
    busy: false,
  };

  const byId = (id) => document.getElementById(id);
  const uploadCard = byId("uploadCard");
  const pdfUpload = byId("pdfUpload");
  const choosePdf = byId("choosePdf");
  const pipelineStatus = byId("pipelineStatus");
  const pipelineStatusText = byId("pipelineStatusText");
  const replacePdf = byId("replacePdf");
  const liveLesson = byId("liveLesson");
  const prototypeBadge = document.querySelector(".proto");

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function asList(value) {
    return Array.isArray(value) ? value : [];
  }

  function pageRange(pages) {
    const values = [...new Set(asList(pages).map(Number).filter((n) => n > 0))]
      .sort((a, b) => a - b);
    if (!values.length) return "Không có slide nguồn";
    const ranges = [];
    let start = values[0];
    let previous = values[0];
    for (const page of values.slice(1)) {
      if (page === previous + 1) {
        previous = page;
        continue;
      }
      ranges.push(start === previous ? `${start}` : `${start}–${previous}`);
      start = previous = page;
    }
    ranges.push(start === previous ? `${start}` : `${start}–${previous}`);
    return `Slide ${ranges.join(", ")}`;
  }

  function listHtml(values) {
    const items = asList(values);
    if (!items.length) return '<span class="hint">Không có.</span>';
    return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }

  function evaluationRows(label, values, kind, icon) {
    return asList(values).map((value) => (
      `<div class="vline ${kind}"><span class="g">${icon}</span>` +
      `<div><b>${label}:</b> ${escapeHtml(value)}</div></div>`
    )).join("");
  }

  function setStatus(mode, text, retry = null) {
    pipelineStatus.className = `pipeline-status ${mode || ""}`.trim();
    pipelineStatusText.textContent = text;
    pipelineStatus.querySelector(".pipeline-retry")?.remove();
    LIVE.retry = retry;
    if (retry) {
      const button = document.createElement("button");
      button.className = "pipeline-retry";
      button.type = "button";
      button.textContent = "Thử lại";
      button.addEventListener("click", retry);
      pipelineStatus.appendChild(button);
    }
    uploadCard.classList.toggle("busy", mode === "busy");
  }

  function setBusy(busy) {
    LIVE.busy = busy;
    choosePdf.disabled = busy;
    byId("startRead").disabled = busy;
    replacePdf.disabled = busy;
  }

  async function apiRequest(path, options = {}, timeoutMs = 180000) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);
    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, {
        ...options,
        signal: controller.signal,
        headers: {
          Accept: "application/json",
          ...(options.headers || {}),
        },
      });
    } catch (error) {
      if (error?.name === "AbortError") {
        throw new LiveApiError(
          "Backend xử lý quá thời gian. Bạn có thể thử lại bước này.",
          "BACKEND_TIMEOUT",
        );
      }
      throw new LiveApiError(
        "Không kết nối được backend. Kiểm tra backend đang chạy rồi thử lại.",
        "BACKEND_UNAVAILABLE",
      );
    } finally {
      window.clearTimeout(timer);
    }

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      throw new LiveApiError(
        `Backend trả về dữ liệu không hợp lệ (HTTP ${response.status}).`,
        "INVALID_BACKEND_RESPONSE",
        response.status,
      );
    }
    if (!response.ok) {
      const error = payload && typeof payload === "object" ? payload.error : null;
      throw new LiveApiError(
        error?.message || `Backend trả về HTTP ${response.status}.`,
        error?.code || "BACKEND_REQUEST_FAILED",
        response.status,
      );
    }
    return payload;
  }

  async function checkBackend() {
    try {
      await apiRequest("/health", {}, 5000);
      setStatus("ok", "Backend đã kết nối · sẵn sàng nhận PDF");
    } catch (error) {
      setStatus(
        "error",
        `${error.message} (${error.code})`,
        checkBackend,
      );
    }
  }

  function resetLiveState(file) {
    if (LIVE.pdfUrl) URL.revokeObjectURL(LIVE.pdfUrl);
    LIVE.active = false;
    LIVE.file = file;
    LIVE.pdfUrl = URL.createObjectURL(file);
    LIVE.document = null;
    LIVE.processing = null;
    LIVE.units = [];
    LIVE.activeUnit = null;
    LIVE.currentPage = 1;
    LIVE.sessions = new Map();
    replacePdf.classList.add("hide");
  }

  async function uploadDocument() {
    const form = new FormData();
    form.append("file", LIVE.file, LIVE.file.name);
    return apiRequest(
      "/documents/upload",
      { method: "POST", body: form },
      60000,
    );
  }

  async function processDocument() {
    return apiRequest(
      `/documents/${encodeURIComponent(LIVE.document.id)}/process`,
      { method: "POST" },
      300000,
    );
  }

  async function runPipeline() {
    if (!LIVE.file || LIVE.busy) return;
    setBusy(true);
    try {
      if (!LIVE.document) {
        setStatus("busy", "1/3 · Đang upload PDF…");
        LIVE.document = await uploadDocument();
      }
      if (!LIVE.processing) {
        setStatus("busy", "2/3 · Đang đọc slide và tạo Knowledge Map…");
        LIVE.processing = await processDocument();
        LIVE.units = asList(LIVE.processing.knowledge_units);
      }
      if (!LIVE.units.length) {
        throw new LiveApiError(
          "Backend không tạo được Knowledge Unit nào.",
          "NO_VALID_KNOWLEDGE_UNITS",
        );
      }

      const coverage = LIVE.processing.coverage || {};
      setStatus(
        "ok",
        `Đã tạo ${LIVE.units.length} Knowledge Units · coverage ` +
          `${Math.round(Number(coverage.coverage_ratio || 0) * 100)}%`,
      );
      openLiveReader();
      await selectLiveUnit(LIVE.units[0].id);
    } catch (error) {
      const safeError = error instanceof LiveApiError
        ? error
        : new LiveApiError("Pipeline gặp lỗi không xác định.");
      setStatus(
        "error",
        `${safeError.message} (${safeError.code})`,
        runPipeline,
      );
      if (LIVE.processing) showPanelError(safeError, runPipeline);
    } finally {
      setBusy(false);
    }
  }

  async function beginLiveFile(file) {
    if (!file) return;
    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setStatus("error", "Chỉ hỗ trợ file PDF.");
      return;
    }
    resetLiveState(file);
    go("course");
    setStatus("busy", `Đã chọn ${file.name} · chuẩn bị upload…`);
    await runPipeline();
  }

  function renderLiveSide() {
    const doc = LIVE.processing?.document || LIVE.document || {};
    byId("sideList").innerHTML = `
      <div class="live-doc-head">
        <b>${escapeHtml(doc.filename || LIVE.file?.name || "Slide PDF")}</b>
        <span>${escapeHtml(doc.page_count || "—")} trang · ${LIVE.units.length} Knowledge Units</span>
      </div>
      ${LIVE.units.map((unit, index) => `
        <button class="live-ku ${unit.id === LIVE.activeUnit?.id ? "on" : ""}"
                type="button" data-live-unit="${escapeHtml(unit.id)}">
          <small>KU${index + 1}</small>
          <b>${escapeHtml(unit.title || `Knowledge Unit ${index + 1}`)}</b>
          <span>${escapeHtml(pageRange(unit.source_pages))}</span>
        </button>
      `).join("")}
    `;
    byId("sideList").querySelectorAll("[data-live-unit]").forEach((button) => {
      button.addEventListener("click", () => selectLiveUnit(button.dataset.liveUnit));
    });
  }

  function showLivePage(page) {
    const total = Number(LIVE.processing?.document?.page_count || 1);
    LIVE.currentPage = Math.max(1, Math.min(total, Number(page) || 1));
    byId("pvNum").textContent = String(LIVE.currentPage);
    byId("pvTot").textContent = String(total);
    byId("notecount").textContent = `Trang ${LIVE.currentPage} · slide nguồn`;
    byId("pagewrap").innerHTML = `
      <div class="pg" data-n="${LIVE.currentPage}">
        <div class="pgmeta">
          <span>Trang ${LIVE.currentPage} / ${total}</span>
          <span>${escapeHtml(LIVE.file?.name || "")}</span>
        </div>
        <div class="live-pdf-shell">
          <iframe title="Slide PDF trang ${LIVE.currentPage}"
            src="${LIVE.pdfUrl}#page=${LIVE.currentPage}&zoom=page-width&toolbar=0"></iframe>
        </div>
      </div>
    `;
    byId("ph_tag").textContent = `Trang ${LIVE.currentPage}`;
  }

  function renderLesson(unit) {
    const index = LIVE.units.findIndex((item) => item.id === unit.id) + 1;
    liveLesson.classList.remove("hide");
    liveLesson.innerHTML = `
      <div class="ku-label">Knowledge Unit ${index} · ${escapeHtml(pageRange(unit.source_pages))}</div>
      <h3>${escapeHtml(unit.title || "Knowledge Unit")}</h3>
      <p>${escapeHtml(unit.summary || "")}</p>
      <h5>Mục tiêu học tập</h5>
      ${listHtml(unit.learning_objectives)}
      <h5>Khái niệm chính</h5>
      ${listHtml(unit.key_concepts)}
      ${asList(unit.common_misconceptions).length ? `
        <h5>Hiểu lầm thường gặp</h5>
        ${listHtml(unit.common_misconceptions)}
      ` : ""}
    `;
  }

  function setPanelForUnit(unit) {
    chat.classList.add("hide");
    recall.classList.remove("hide");
    composer.classList.add("hide");
    ph_title.textContent = unit.title || "Auto Learning";
    ph_sub.textContent = "Lesson và câu hỏi theo slide";
    ph_tag.textContent = pageRange(unit.source_pages);
    quota.innerHTML = `
      <div class="r"><span>Knowledge Unit đang học</span><span class="free">đã nối backend</span></div>
      <div class="bar"><i style="width:100%"></i></div>
    `;
    renderLesson(unit);
    rc_ask.classList.remove("hide");
    rc_out.classList.add("hide");
    rc_q.innerHTML = '<div class="live-loading">Đang tạo learning session và nạp câu hỏi đầu tiên…</div>';
    rc_in.value = "";
    rc_in.disabled = true;
    rc_send.disabled = true;
  }

  function renderQuestion(next) {
    const question = next?.question;
    rc_out.classList.add("hide");
    rc_ask.classList.remove("hide");
    if (!question) {
      rc_q.innerHTML = '<div class="live-loading">Knowledge Unit này hiện không còn câu hỏi tiếp theo.</div>';
      rc_in.value = "";
      rc_in.disabled = true;
      rc_send.disabled = true;
      return;
    }
    rc_q.textContent = question.question_text;
    rc_in.value = "";
    rc_in.disabled = false;
    rc_send.disabled = false;
    rc_in.dataset.questionId = question.id;
    rc_in.placeholder = "Gõ bằng lời của bạn…";
    window.setTimeout(() => rc_in.focus(), 80);
  }

  async function selectLiveUnit(unitId) {
    const unit = LIVE.units.find((item) => item.id === unitId);
    if (!unit || LIVE.busy) return;
    LIVE.activeUnit = unit;
    renderLiveSide();
    showLivePage(asList(unit.source_pages)[0] || 1);
    setPanelForUnit(unit);
    setBusy(true);
    try {
      let sessionState = LIVE.sessions.get(unit.id);
      if (!sessionState) {
        const session = await apiRequest(
          "/learning-sessions",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: "local-user",
              document_id: LIVE.processing.document.id,
              knowledge_unit_id: unit.id,
            }),
          },
          240000,
        );
        sessionState = { session, next: null };
        LIVE.sessions.set(unit.id, sessionState);
      }
      sessionState.next = await apiRequest(
        `/learning-sessions/${encodeURIComponent(sessionState.session.id)}/next-question`,
      );
      renderQuestion(sessionState.next);
    } catch (error) {
      const safeError = error instanceof LiveApiError
        ? error
        : new LiveApiError("Không tạo được learning session.");
      showPanelError(safeError, () => selectLiveUnit(unit.id));
    } finally {
      setBusy(false);
    }
  }

  function showPanelError(error, retry) {
    chat.classList.add("hide");
    recall.classList.remove("hide");
    composer.classList.add("hide");
    rc_ask.classList.add("hide");
    rc_out.classList.remove("hide");
    rc_out.innerHTML = `
      <div class="live-error">
        <b>Không thể tiếp tục.</b><br>
        ${escapeHtml(error.message)}<br>
        <small>Error code: ${escapeHtml(error.code)}</small>
      </div>
      <div class="acts" style="margin-top:14px">
        <button class="btn-primary" id="liveRetryPanel" type="button">Thử lại bước bị lỗi</button>
      </div>
    `;
    byId("liveRetryPanel").addEventListener("click", retry);
  }

  function recordLiveResult(result) {
    const score = Number(result?.evaluation?.overall_score || 0);
    const done = score >= 0.75;
    done ? S.said++ : S.blank++;
    S.notes++;
    const pages = asList(LIVE.activeUnit?.source_pages);
    S.rows = S.rows.filter((row) => row.doc !== LIVE.processing.document.id ||
      row.title !== LIVE.activeUnit.title);
    S.rows.unshift({
      doc: LIVE.processing.document.id,
      pg: pages[0] || 1,
      title: LIVE.activeUnit.title,
      detail: `${Math.round(score * 100)}% · ${result.evaluation.feedback}`,
      state: done ? "said" : "blank",
    });
    home_said.textContent = `${S.said}/${Math.max(S.said + S.blank, 1)}`;
  }

  function renderFeedback(result, next, nextError = null) {
    const evaluation = result.evaluation || {};
    const mastery = result.mastery || {};
    const overall = Math.round(Number(evaluation.overall_score || 0) * 100);
    const masteryPercent = Math.round(Number(mastery.mastery_score || 0) * 100);
    rc_ask.classList.add("hide");
    rc_out.classList.remove("hide");
    rc_out.innerHTML = `
      <div class="mastery-line"><span>Mastery của Knowledge Unit</span><b>${masteryPercent}%</b></div>
      <div class="score">${overall}% · ${escapeHtml(evaluation.feedback || "Đã chấm câu trả lời.")}</div>
      ${evaluationRows("Bạn đã nắm", evaluation.correct_points, "ok", "✅")}
      ${evaluationRows("Bạn chưa nhắc tới", evaluation.missing_points, "miss", "⭕")}
      ${evaluationRows("Điểm chưa đúng", evaluation.incorrect_points, "miss", "⚠️")}
      ${evaluationRows("Hiểu lầm được phát hiện", evaluation.detected_misconceptions, "miss", "🧭")}
      ${nextError ? `<div class="live-error">${escapeHtml(nextError.message)}</div>` : ""}
      <div class="acts" style="margin-top:14px">
        ${next?.question
          ? '<button class="btn-primary" id="liveNextQuestion" type="button">Câu hỏi tiếp theo</button>'
          : nextError
            ? '<button class="btn-primary" id="liveRetryNext" type="button">Nạp lại câu tiếp theo</button>'
            : '<button class="btn-primary" id="liveChooseNextKu" type="button">Chọn Knowledge Unit khác</button>'}
      </div>
      <div class="fb"><span>Phản hồi được tạo từ rubric và slide nguồn.</span></div>
    `;
    byId("liveNextQuestion")?.addEventListener("click", () => renderQuestion(next));
    byId("liveRetryNext")?.addEventListener("click", async () => {
      await loadNextAfterAnswer(LIVE.sessions.get(LIVE.activeUnit.id), result);
    });
    byId("liveChooseNextKu")?.addEventListener("click", () => {
      const index = LIVE.units.findIndex((unit) => unit.id === LIVE.activeUnit.id);
      const candidate = LIVE.units[index + 1] || LIVE.units[0];
      selectLiveUnit(candidate.id);
    });
  }

  async function loadNextAfterAnswer(sessionState, result) {
    try {
      const next = await apiRequest(
        `/learning-sessions/${encodeURIComponent(sessionState.session.id)}/next-question`,
      );
      sessionState.next = next;
      renderFeedback(result, next);
    } catch (error) {
      const safeError = error instanceof LiveApiError
        ? error
        : new LiveApiError("Không nạp được câu hỏi tiếp theo.");
      renderFeedback(result, null, safeError);
    }
  }

  async function submitLiveAnswer() {
    const answer = rc_in.value.trim();
    const questionId = rc_in.dataset.questionId;
    if (!answer || !questionId || LIVE.busy) return;
    const sessionState = LIVE.sessions.get(LIVE.activeUnit.id);
    setBusy(true);
    rc_in.disabled = true;
    rc_send.disabled = true;
    rc_send.textContent = "Đang chấm…";
    try {
      const result = await apiRequest(
        `/learning-sessions/${encodeURIComponent(sessionState.session.id)}/answers`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question_id: questionId,
            user_answer: answer,
          }),
        },
        240000,
      );
      recordLiveResult(result);
      await loadNextAfterAnswer(sessionState, result);
    } catch (error) {
      const safeError = error instanceof LiveApiError
        ? error
        : new LiveApiError("Không chấm được câu trả lời.");
      showPanelError(safeError, submitLiveAnswer);
      rc_in.disabled = false;
    } finally {
      rc_send.textContent = "Gửi";
      setBusy(false);
    }
  }

  function openLiveReader() {
    LIVE.active = true;
    S.doc = "__live__";
    rdTitle.textContent = LIVE.processing.document.filename;
    rdCode.textContent = `AUTO LEARNING · ${LIVE.units.length} KNOWLEDGE UNITS`;
    replacePdf.classList.remove("hide");
    prototypeBadge.textContent = "PROTOTYPE · BACKEND ĐÃ KẾT NỐI";
    byId("pagewrap").classList.add("live-mode");
    byId("selpop").classList.remove("show");
    renderLiveSide();
    showLivePage(1);
    go("reader");
  }

  choosePdf.addEventListener("click", () => pdfUpload.click());
  byId("startRead").onclick = () => pdfUpload.click();
  replacePdf.addEventListener("click", () => pdfUpload.click());
  pdfUpload.addEventListener("change", () => beginLiveFile(pdfUpload.files?.[0]));

  ["dragenter", "dragover"].forEach((eventName) => {
    uploadCard.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadCard.classList.add("dragging");
    });
  });
  ["dragleave", "drop"].forEach((eventName) => {
    uploadCard.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadCard.classList.remove("dragging");
    });
  });
  uploadCard.addEventListener("drop", (event) => {
    beginLiveFile(event.dataTransfer?.files?.[0]);
  });

  const demoSend = rc_send.onclick;
  rc_send.onclick = () => LIVE.active ? submitLiveAnswer() : demoSend();
  const demoSkip = rc_skip.onclick;
  rc_skip.onclick = () => {
    if (!LIVE.active) {
      demoSkip();
      return;
    }
    rd.classList.remove("panel-open");
  };
  pvPrev.onclick = () => LIVE.active
    ? showLivePage(LIVE.currentPage - 1)
    : step(-1);
  pvNext.onclick = () => LIVE.active
    ? showLivePage(LIVE.currentPage + 1)
    : step(1);

  checkBackend();
})();
