import { useSessions } from './hooks/useSessions';
import { useChat } from './hooks/useChat';
import SessionSidebar from './components/SessionSidebar';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import './index.css';

function App() {
  const {
    sessions,
    activeSessionId,
    setActiveSessionId,
    createSession,
    deleteSession,
    loading: sessionsLoading,
  } = useSessions();

  const {
    messages,
    loading: chatLoading,
    awaitingConfirmation,
    extractedData,
    error,
    sendMessage,
    uploadImage,
    uploadAudio,
    confirmContact,
    clearChat,
  } = useChat(activeSessionId);

  const handleSelectSession = (sessionId) => {
    clearChat();
    setActiveSessionId(sessionId);
  };

  const handleCreateSession = async () => {
    clearChat();
    await createSession();
  };

  const handleConfirm = (edits) => {
    confirmContact(true, edits);
  };

  const handleReject = () => {
    confirmContact(false);
  };

  return (
    <div className="app-container">
      <SessionSidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
        onDeleteSession={deleteSession}
        loading={sessionsLoading}
      />

      <main className="main-content">
        <div className="chat-header">
          <div className="chat-header-title">
            {activeSessionId ? `Session` : 'LeadSync Agent'}
          </div>
          <div className="chat-header-status">
            <div className="status-dot" />
            <span>Online</span>
          </div>
        </div>

        {activeSessionId ? (
          <>
            <ChatWindow
              messages={messages}
              loading={chatLoading}
              awaitingConfirmation={awaitingConfirmation}
              extractedData={extractedData}
              onConfirm={handleConfirm}
              onReject={handleReject}
            />
            <InputBar
              onSendMessage={sendMessage}
              onUploadImage={uploadImage}
              onUploadAudio={uploadAudio}
              loading={chatLoading}
              disabled={awaitingConfirmation}
            />
          </>
        ) : (
          <div className="empty-state">
            <div className="empty-state-icon">⚡</div>
            <div className="empty-state-title">LeadSync Agent</div>
            <div className="empty-state-text">
              AI-powered visiting card digitization and contact management.
              Create a new session or select an existing one to get started.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
