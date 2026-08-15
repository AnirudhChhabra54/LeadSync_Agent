import React from 'react';

export default function HUDStatusBar({ activeSessionId, messageCount = 0 }) {
  return (
    <footer className="hud-status-bar">
      <div className="hud-left-stats">
        <div className="hud-stat-item">
          <span className="hud-indicator bg-emerald-400" />
          <span className="hud-key">CRM TARGET:</span>
          <span className="hud-value text-emerald-400 font-mono">Google Sheets (Connected)</span>
        </div>

        <div className="hud-divider" />

        <div className="hud-stat-item hidden-mobile">
          <span className="hud-indicator bg-cyan-400" />
          <span className="hud-key">VISION MODEL:</span>
          <span className="hud-value font-mono">Gemini 1.5 Flash</span>
        </div>

        <div className="hud-divider hidden-mobile" />

        <div className="hud-stat-item hidden-mobile">
          <span className="hud-indicator bg-purple-400" />
          <span className="hud-key">STORAGE CDN:</span>
          <span className="hud-value font-mono">Cloudinary Secure</span>
        </div>
      </div>

      <div className="hud-right-stats">
        <div className="hud-stat-item">
          <span className="hud-key">SESSION:</span>
          <span className="hud-value font-mono text-cyan-300">
            {activeSessionId ? activeSessionId.slice(0, 8) : 'DISCONNECTED'}
          </span>
        </div>
        <div className="hud-pill-badge">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span>HITL GATE READY</span>
        </div>
      </div>
    </footer>
  );
}
