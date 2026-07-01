import { useState } from 'react';

export default function SessionSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  loading,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">⚡</div>
          <span className="sidebar-logo-text">LeadSync</span>
        </div>
        <button
          className="new-session-btn"
          onClick={onCreateSession}
          disabled={loading}
        >
          <span>＋</span> New Session
        </button>
      </div>

      <div className="session-list">
        {sessions.length === 0 && !loading && (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
            No sessions yet. Create one to get started.
          </div>
        )}
        {sessions.map((session) => (
          <div
            key={session.session_id}
            className={`session-item ${activeSessionId === session.session_id ? 'active' : ''}`}
            onClick={() => onSelectSession(session.session_id)}
          >
            <div className="session-item-content">
              <div className="session-item-title">
                {session.title || 'New Session'}
              </div>
              <div className="session-item-meta">
                {session.message_count || 0} messages
                {session.has_pending_contact && ' • 🎙️ awaiting voice note'}
              </div>
            </div>
            <button
              className="session-delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.session_id);
              }}
              title="Delete session"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}
