import { useState } from 'react';

export default function ConfirmCard({ extractedData, onConfirm, onReject, loading }) {
  const [edits, setEdits] = useState({
    name: extractedData?.name || '',
    phone: extractedData?.phone || '',
    email: extractedData?.email || '',
    company: extractedData?.company || '',
    designation: extractedData?.designation || '',
    website_linkedin: extractedData?.website_linkedin || '',
  });

  const handleChange = (field, value) => {
    setEdits((prev) => ({ ...prev, [field]: value }));
  };

  const handleConfirm = () => {
    const changes = {};
    Object.keys(edits).forEach((key) => {
      if (edits[key] !== (extractedData?.[key] || '')) {
        changes[key] = edits[key];
      }
    });
    onConfirm(changes);
  };

  const fields = [
    { key: 'name', label: 'Full Name', conf: '99%', icon: 'user' },
    { key: 'phone', label: 'Phone Number', conf: '98%', icon: 'phone' },
    { key: 'email', label: 'Corporate Email', conf: '99%', icon: 'mail' },
    { key: 'company', label: 'Organization', conf: '97%', icon: 'building' },
    { key: 'designation', label: 'Designation / Title', conf: '95%', icon: 'badge' },
    { key: 'website_linkedin', label: 'Website / LinkedIn URL', conf: '92%', icon: 'link' },
  ];

  return (
    <div className="hitl-confirm-glass-card">
      {/* Top Banner */}
      <div className="hitl-header">
        <div className="hitl-title-group">
          <div className="hitl-badge-icon">
            <svg className="w-4 h-4 text-pink-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div>
            <h4 className="hitl-title">Human-in-the-Loop Validation Gate</h4>
            <p className="hitl-desc">
              Review Gemini 1.5 OCR extracted data. Make modifications if required before syncing to Google Sheets CRM.
            </p>
          </div>
        </div>

        <div className="hitl-status-flag">
          <span className="pulse-ping-rose" />
          <span>Manual Review</span>
        </div>
      </div>

      {/* Grid of Fields */}
      <div className="hitl-fields-grid">
        {fields.map(({ key, label, conf }) => (
          <div className="hitl-field-item" key={key}>
            <div className="hitl-field-header">
              <label className="hitl-label">{label}</label>
              <span className="hitl-conf-badge">
                <span className="conf-dot" />
                {conf} match
              </span>
            </div>
            <div className="hitl-input-wrapper">
              <input
                type="text"
                value={edits[key]}
                onChange={(e) => handleChange(key, e.target.value)}
                placeholder={`Enter ${label.toLowerCase()}...`}
                className="hitl-input"
              />
              <span className="input-focus-glow" />
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons Bar */}
      <div className="hitl-actions-bar">
        <button
          className="hitl-btn-confirm"
          onClick={handleConfirm}
          disabled={loading}
        >
          {loading ? (
            <span className="loading-spinner-ring small" />
          ) : (
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          )}
          <span>{loading ? 'Writing to CRM...' : 'Confirm & Sync to Google Sheets'}</span>
        </button>

        <button
          className="hitl-btn-reject"
          onClick={onReject}
          disabled={loading}
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
          <span>Reject Inbound Lead</span>
        </button>
      </div>
    </div>
  );
}
