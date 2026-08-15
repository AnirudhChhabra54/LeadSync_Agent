import { useState, useRef } from 'react';

export default function InputBar({
  onSendMessage,
  onUploadImage,
  onUploadAudio,
  loading,
  disabled,
}) {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const handleSend = () => {
    if (!text.trim() || loading || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadImage(file);
      e.target.value = '';
    }
  };

  // Start recording audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], `voice_note_${Date.now()}.webm`, {
          type: 'audio/webm',
        });
        onUploadAudio(audioFile);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingSeconds(0);

      timerRef.current = setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('Audio recording failed:', err);
      alert('Microphone access is required to record voice notes.');
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const formatSeconds = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="input-command-bar">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/webp"
        onChange={handleFileChange}
        className="hidden"
      />

      {isRecording ? (
        /* Active Recording Soundwave HUD */
        <div className="recording-hud-bar">
          <div className="flex items-center gap-3">
            <span className="recording-pulse-beacon" />
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-rose-400">Recording Voice Debrief</span>
              <span className="text-[10px] text-gray-400 font-mono">{formatSeconds(recordingSeconds)} • Live Audio Buffer</span>
            </div>
          </div>

          {/* Soundwave equalizer visualizer bars */}
          <div className="soundwave-equalizer">
            <span className="eq-bar eq-1" />
            <span className="eq-bar eq-2" />
            <span className="eq-bar eq-3" />
            <span className="eq-bar eq-4" />
            <span className="eq-bar eq-5" />
            <span className="eq-bar eq-6" />
            <span className="eq-bar eq-7" />
            <span className="eq-bar eq-8" />
          </div>

          <button className="stop-recording-btn" onClick={stopRecording}>
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            <span>Finish & Transcribe</span>
          </button>
        </div>
      ) : (
        /* Regular Input Console */
        <div className="input-box-wrapper">
          <button
            type="button"
            className="input-tool-btn"
            title="Upload Business Card"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || disabled}
          >
            <svg className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
            <span className="tooltip-tag">Upload Card Image</span>
          </button>

          <button
            type="button"
            className="input-tool-btn voice-btn"
            title="Record Voice Note"
            onClick={startRecording}
            disabled={loading || disabled}
          >
            <svg className="w-5 h-5 text-pink-400 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
            <span className="tooltip-tag">Record Meeting Audio</span>
          </button>

          <input
            type="text"
            placeholder={disabled ? 'Action required in confirmation dialog above...' : 'Type a query or prompt (e.g. "Review lead from Acme Corp")...'}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading || disabled}
            className="input-text-field"
          />

          <button
            type="button"
            className="input-send-btn"
            onClick={handleSend}
            disabled={!text.trim() || loading || disabled}
            title="Send Message"
          >
            {loading ? (
              <span className="loading-spinner-ring small" />
            ) : (
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
