// API client — maps 1-1 to FastAPI endpoints at /api (proxied to localhost:8000)

const BASE = import.meta.env.VITE_API_URL || '/api';

async function request(method, path, body, isFormData = false) {
  const opts = { method, headers: {} };
  if (body && !isFormData) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  } else if (isFormData) {
    opts.body = body; // FormData — browser sets Content-Type automatically
  }

  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail || err.message || detail;
    } catch (_) {}
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return null;
  return res.json();
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

// ── Health ────────────────────────────────────────────────────────
export async function checkHealth() {
  return request('GET', '/health');
}

// ── Documents ────────────────────────────────────────────────────
export async function uploadDocument(file) {
  const form = new FormData();
  form.append('file', file);
  return request('POST', '/documents/upload', form, true);
}

export async function processDocument(documentId) {
  return request('POST', `/documents/${documentId}/process`);
}

export async function getDocument(documentId) {
  return request('GET', `/documents/${documentId}`);
}

export async function listDocuments() {
  return request('GET', '/documents');
}

// ── Knowledge Map ────────────────────────────────────────────────
export async function getKnowledgeMap(documentId) {
  return request('GET', `/documents/${documentId}/knowledge-map`);
}

export async function getKnowledgeUnit(unitId) {
  return request('GET', `/knowledge-units/${unitId}`);
}

// ── Learning Sessions ─────────────────────────────────────────────
export async function createLearningSession(documentId, knowledgeUnitId = null) {
  return request('POST', '/learning-sessions', {
    user_id: 'local-user',
    document_id: documentId,
    knowledge_unit_id: knowledgeUnitId,
  });
}

export async function getNextQuestion(sessionId) {
  return request('GET', `/learning-sessions/${sessionId}/next-question`);
}

export async function submitAnswer(sessionId, questionId, userAnswer) {
  return request('POST', `/learning-sessions/${sessionId}/answers`, {
    question_id: questionId,
    user_answer: userAnswer,
  });
}

// ── Progress ──────────────────────────────────────────────────────
export async function getUserProgress() {
  return request('GET', '/progress/local-user');
}

export async function getUnitProgress(unitId) {
  return request('GET', `/progress/local-user/units/${unitId}`);
}

// ── Tutor Agent ───────────────────────────────────────────────────
export async function runTutorAgent(sessionId, questionId, misconception, userMessage, history = []) {
  return request('POST', '/agents/tutor', {
    session_id: sessionId,
    question_id: questionId,
    misconception,
    user_message: userMessage,
    conversation_history: history,
  });
}
