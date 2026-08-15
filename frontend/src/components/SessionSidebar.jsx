import { useState, useMemo } from 'react';

export default function SessionSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  loading,
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const q = searchQuery.toLowerCase();
    return sessions.filter((s) => {
      const title = (s.title || 'New Session').toLowerCase();
      const id = (s.session_id || '').toLowerCase();
      return title.includes(q) || id.includes(q);
    });
  }, [sessions, searchQuery]);

  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return 'Just now';
    try {
      const d = new Date(dateStr);
      const now = new Date();
      const diffMs = now - d;
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return `${Math.floor(diffHours / 24)}d ago`;
    } catch {
      return 'Recent';
    }
  };

  return (
    <aside className="sidebar-command-center">
      {/* Top action block */}
      <div className="sidebar-top-section">
        <div className="sidebar-action-header">
          <div className="flex items-center justify-between w-full mb-3">
            <span className="sidebar-section-title">Session Threads</span>
            <span className="sidebar-count-chip">{sessions.length} Threads</span>
          </div>

          <button
            className="new-session-glow-btn"
            onClick={onCreateSession}
            disabled={loading}
          >
            <svg className="w-4 h-4 text-cyan-400 group-hover:rotate-90 transition-transform duration-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Launch Ingestion Thread</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="sidebar-search-box">
          <svg className="w-3.5 h-3.5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search leads or sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button className="clear-search-btn" onClick={() => setSearchQuery('')}>
              ×
            </button>
          )}
        </div>
      </div>

      {/* Session list stream */}
      <div className="sidebar-session-stream">
        {loading && sessions.length === 0 ? (
          <div className="sidebar-empty-state">
            <div className="loading-spinner-ring" />
            <span>Loading threads...</span>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="sidebar-empty-state">
            <svg className="w-8 h-8 text-gray-500 opacity-60 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p className="text-xs text-gray-400">{searchQuery ? 'No matching threads found' : 'No active sessions yet'}</p>
            <p className="text-[11px] text-gray-500 mt-1">Click above to start a new lead ingestion</p>
          </div>
        ) : (
          filteredSessions.map((session) => {
            const isActive = session.session_id === activeSessionId;
            const hasPending = session.has_pending_contact;
            const msgCount = session.message_count || 0;

            return (
              <div
                key={session.session_id}
                className={`sidebar-session-card ${isActive ? 'active' : ''}`}
                onClick={() => onSelectSession(session.session_id)}
              >
                <div className="card-leading-indicator">
                  {isActive ? (
                    <span className="active-glow-bar" />
                  ) : (
                    <span className="idle-indicator-dot" />
                  )}
                </div>

                <div className="card-info-wrap">
                  <div className="card-title-row">
                    <span className="card-title-text">{session.title || 'Lead Ingestion'}</span>
                    {hasPending ? (
                      <span className="status-tag-review">Review Required</span>
                    ) : msgCount > 0 ? (
                      <span className="status-tag-synced">Active</span>
                    ) : (
                      <span className="status-tag-new">New</span>
                    )}
                  </div>

                  <div className="card-meta-row">
                    <span className="card-time-text">{formatTimeAgo(session.updated_at || session.created_at)}</span>
                    <span className="card-dot-sep">•</span>
                    <span className="card-id-text">ID: {session.session_id.slice(0, 8)}</span>
                  </div>
                </div>

                <button
                  className="sidebar-delete-action"
                  title="Purge session"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm('Delete this session thread?')) {
                      onDeleteSession(session.session_id);
                    }
                  }}
                >
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Sidebar Footer info */}
      <div className="sidebar-bottom-panel">
        <div className="flex items-center gap-2 text-[11px] text-gray-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>MongoDB Atlas Connected</span>
        </div>
        <span className="text-[10px] font-mono text-gray-500">v1.2.4</span>
      </div>
    </aside>
  );
}
