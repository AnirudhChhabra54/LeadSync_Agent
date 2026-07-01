import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ConfirmCard from './ConfirmCard';

export default function ChatWindow({
  messages,
  loading,
  awaitingConfirmation,
  extractedData,
  onConfirm,
  onReject,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, awaitingConfirmation]);

  return (
    <div className="messages-container">
      {messages.length === 0 && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">📇</div>
          <div className="empty-state-title">Welcome to LeadSync</div>
          <div className="empty-state-text">
            Upload a visiting card image to extract contact information,
            or send a message to get started. I'll help you digitize contacts
            and organize them in Google Sheets.
          </div>
        </div>
      )}

      {messages.map((msg, index) => (
        <MessageBubble key={index} message={msg} />
      ))}

      {awaitingConfirmation && extractedData && (
        <ConfirmCard
          extractedData={extractedData}
          onConfirm={onConfirm}
          onReject={onReject}
          loading={loading}
        />
      )}

      {loading && !awaitingConfirmation && (
        <div className="typing-indicator">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
