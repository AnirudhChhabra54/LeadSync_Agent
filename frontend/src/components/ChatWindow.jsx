import { useRef, useEffect } from 'react';
import MessageBubble from './chat/MessageBubble';
import ConfirmCard from './chat/ConfirmCard';
import ParticleText from './text/ParticleText';

export default function ChatWindow({
  messages,
  loading,
  awaitingConfirmation,
  extractedData,
  onConfirm,
  onReject,
  onUploadImageTrigger,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, awaitingConfirmation]);

  return (
    <div className="chat-window-viewport">
      {/* Empty State / Welcome Cockpit */}
      {messages.length === 0 && !loading && (
        <div className="chat-welcome-cockpit">
          <div className="cockpit-gem-icon">
            <svg className="w-8 h-8 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
            <span className="cockpit-glow" />
          </div>

          {/* Interactive Particle Text Title */}
          <div style={{ width: '100%', height: 220, position: 'relative', background: 'transparent', marginBottom: 12 }}>
            <ParticleText
              text="LeadSync Cockpit"
              particleSize={2.2}
              density={4}
              color="#f8fafc"
              highlightColor="#00e5ff"
              scatter={190}
              gatherDuration={1600}
              stagger={420}
              pointerRepel={42}
              repelRadius={120}
              idleDrift={0.8}
              trigger="mount"
              fontSize="clamp(2.2rem, 5vw, 4rem)"
              fontWeight={800}
              fontFamily="inherit"
              glow
            />
          </div>

          <p className="cockpit-subtitle">
            Autonomous multimodal agent for digitizing physical visiting cards, enriching corporate intelligence, and appending meeting voice debriefs directly into Google Sheets CRM.
          </p>

          <div className="cockpit-quick-grid">
            <div className="quick-action-card">
              <div className="quick-icon text-cyan-400">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>
              <span className="quick-title">1. Upload Visiting Card</span>
              <span className="quick-desc">Gemini 1.5 Flash extracts Name, Phone, Email, Company & Designation.</span>
            </div>

            <div className="quick-action-card">
              <div className="quick-icon text-pink-400">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <span className="quick-title">2. HITL Approval Gate</span>
              <span className="quick-desc">Review extracted fields and verify or edit details before CRM writing.</span>
            </div>

            <div className="quick-action-card">
              <div className="quick-icon text-emerald-400">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                  <line x1="12" y1="19" x2="12" y2="23" />
                  <line x1="8" y1="23" x2="16" y2="23" />
                </svg>
              </div>
              <span className="quick-title">3. Attach Voice Debrief</span>
              <span className="quick-desc">AI summarizes conversation & uploads audio to Cloudinary CDN.</span>
            </div>
          </div>
        </div>
      )}

      {/* Message Stream */}
      <div className="messages-stream">
        {messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))}
      </div>

      {/* HITL Confirmation Modal */}
      {awaitingConfirmation && extractedData && (
        <ConfirmCard
          extractedData={extractedData}
          onConfirm={onConfirm}
          onReject={onReject}
          loading={loading}
        />
      )}

      {/* Typing & Processing Laser Shimmer */}
      {loading && !awaitingConfirmation && (
        <div className="agent-thinking-banner">
          <div className="scanning-beam-bar" />
          <div className="flex items-center gap-2.5">
            <span className="thinking-spinner" />
            <span className="text-xs font-mono text-cyan-300">LangGraph StateGraph executing node...</span>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
