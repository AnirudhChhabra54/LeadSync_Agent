import { useState, useRef } from 'react';

export default function InputBar({
  onSendMessage,
  onUploadImage,
  onUploadAudio,
  loading,
  disabled,
}) {
  const [text, setText] = useState('');
  const imageInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const handleSend = () => {
    if (text.trim() && !loading && !disabled) {
      onSendMessage(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadImage(file);
      e.target.value = '';
    }
  };

  const handleAudioSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadAudio(file);
      e.target.value = '';
    }
  };

  return (
    <div className="input-bar">
      <div className="input-bar-inner">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Select or create a session to start...' : 'Type a message...'}
          disabled={loading || disabled}
        />

        <div className="input-bar-actions">
          {/* Image upload */}
          <button
            className="icon-btn"
            onClick={() => imageInputRef.current?.click()}
            disabled={loading || disabled}
            title="Upload visiting card image"
          >
            📷
          </button>
          <input
            ref={imageInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/heic"
            onChange={handleImageSelect}
            className="file-input-hidden"
          />

          {/* Audio upload */}
          <button
            className="icon-btn"
            onClick={() => audioInputRef.current?.click()}
            disabled={loading || disabled}
            title="Upload voice note"
          >
            🎙️
          </button>
          <input
            ref={audioInputRef}
            type="file"
            accept="audio/mpeg,audio/mp3,audio/wav,audio/ogg,audio/webm,audio/m4a,audio/mp4"
            onChange={handleAudioSelect}
            className="file-input-hidden"
          />

          {/* Send */}
          <button
            className="icon-btn send-btn"
            onClick={handleSend}
            disabled={!text.trim() || loading || disabled}
            title="Send message"
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
