/**
 * API Client — communicates with the LeadSync FastAPI backend.
 */

const API_BASE = '/api';

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  // ── Sessions ────────────────────────────────────────────────────
  async listSessions() {
    const res = await fetch(`${API_BASE}/sessions`);
    return handleResponse(res);
  },

  async getSession(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    return handleResponse(res);
  },

  async getSessionMessages(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
    return handleResponse(res);
  },

  async createSession() {
    const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' });
    return handleResponse(res);
  },

  async deleteSession(sessionId) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
    return handleResponse(res);
  },

  // ── Chat ────────────────────────────────────────────────────────
  async sendMessage(sessionId, message) {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    return handleResponse(res);
  },

  async confirmContact(sessionId, approved, edits = {}) {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        action: approved ? 'confirm' : 'reject',
        edits,
      }),
    });
    return handleResponse(res);
  },

  async uploadImage(sessionId, file) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/chat/upload-image`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async uploadAudio(sessionId, file) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/chat/upload-audio`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  // ── Health ──────────────────────────────────────────────────────
  async healthCheck() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },
};
