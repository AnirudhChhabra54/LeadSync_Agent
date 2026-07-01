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
    // Only send fields that were actually changed
    const changes = {};
    Object.keys(edits).forEach((key) => {
      if (edits[key] !== (extractedData?.[key] || '')) {
        changes[key] = edits[key];
      }
    });
    onConfirm(changes);
  };

  const fields = [
    { key: 'name', label: 'Name' },
    { key: 'phone', label: 'Phone' },
    { key: 'email', label: 'Email' },
    { key: 'company', label: 'Company' },
    { key: 'designation', label: 'Designation' },
    { key: 'website_linkedin', label: 'Website / LinkedIn' },
  ];

  return (
    <div className="confirm-card">
      <div className="confirm-card-title">
        📋 Confirm Contact Details
      </div>
      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
        Review and edit the extracted information before saving to Google Sheets.
      </p>

      {fields.map(({ key, label }) => (
        <div className="confirm-field" key={key}>
          <label>{label}</label>
          <input
            type="text"
            value={edits[key]}
            onChange={(e) => handleChange(key, e.target.value)}
            placeholder={`Enter ${label.toLowerCase()}`}
          />
        </div>
      ))}

      <div className="confirm-actions">
        <button
          className="btn btn-confirm"
          onClick={handleConfirm}
          disabled={loading}
        >
          ✅ Confirm & Save
        </button>
        <button
          className="btn btn-reject"
          onClick={onReject}
          disabled={loading}
        >
          ✕ Cancel
        </button>
      </div>
    </div>
  );
}
