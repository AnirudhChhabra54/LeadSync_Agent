import React from 'react';

export default function MessageBubble({ message }) {
  const { role, content, timestamp } = message;

  const isUser = role === 'user';
  const isSystem = role === 'system';

  const formatTime = (ts) => {
    if (!ts) return '';
    try {
      return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  // Convert basic markdown asterisks & backticks for clean rendering
  const renderFormattedContent = (text) => {
    if (!text) return null;
    const lines = text.split('\n');

    return lines.map((line, lineIdx) => {
      // Bold rendering
      const parts = line.split(/(\*\*.*?\*\*|`.*?`)/g);

      return (
        <p key={lineIdx} className={line.startsWith('•') || line.startsWith('-') ? 'pl-2 py-0.5' : 'py-0.5'}>
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={pIdx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
            }
            if (part.startsWith('`') && part.endsWith('`')) {
              return <code key={pIdx} className="px-1.5 py-0.5 rounded bg-black/40 text-cyan-300 font-mono text-xs">{part.slice(1, -1)}</code>;
            }
            return part;
          })}
        </p>
      );
    });
  };

  if (isSystem) {
    return (
      <div className="system-msg-banner">
        <span className="system-icon-ping">⚡</span>
        <span className="system-text">{content}</span>
      </div>
    );
  }

  return (
    <div className={`message-row ${isUser ? 'user-align' : 'agent-align'}`}>
      {!isUser && (
        <div className="agent-avatar-gem">
          <svg className="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
        </div>
      )}

      <div className={`message-bubble-glass ${isUser ? 'user-glass' : 'agent-glass'}`}>
        <div className="bubble-header-row">
          <span className="bubble-sender-name">{isUser ? 'Field Executive' : 'LeadSync Agent'}</span>
          {timestamp && <span className="bubble-time">{formatTime(timestamp)}</span>}
        </div>

        <div className="bubble-body-content">
          {renderFormattedContent(content)}
        </div>
      </div>
    </div>
  );
}
