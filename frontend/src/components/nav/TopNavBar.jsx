import React from 'react';

export default function TopNavBar({ activeSessionId, sessionCount = 0 }) {
  return (
    <header className="top-nav-bar">
      <div className="nav-brand">
        <div className="brand-logo-gem">
          <svg className="w-5 h-5 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
          <span className="gem-pulse" />
        </div>
        <div className="brand-titles">
          <span className="brand-name">LeadSync <span className="brand-tag">PRO</span></span>
          <span className="brand-subtitle">Autonomous Multimodal Sales Agent</span>
        </div>
      </div>

      <div className="nav-metrics">
        <div className="metric-pill">
          <span className="status-live-dot" />
          <span className="metric-label">LangGraph Engine</span>
          <span className="metric-val">v1.2 Online</span>
        </div>

        <div className="metric-pill hidden-mobile">
          <svg className="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
          <span className="metric-label">Google Sheets CRM</span>
          <span className="metric-val text-emerald-400">Live Sync</span>
        </div>

        <div className="metric-pill hidden-mobile">
          <svg className="w-3.5 h-3.5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          <span className="metric-label">Gemini 1.5 Flash</span>
          <span className="metric-val text-purple-300">Vision & Audio</span>
        </div>

        <div className="session-badge">
          <span className="badge-dot" />
          <span>{activeSessionId ? 'Thread Active' : 'Select Session'}</span>
        </div>
      </div>
    </header>
  );
}
