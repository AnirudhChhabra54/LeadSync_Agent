import { useSessions } from './hooks/useSessions';
import { useChat } from './hooks/useChat';
import SessionSidebar from './components/SessionSidebar';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import TopNavBar from './components/nav/TopNavBar';
import HUDStatusBar from './components/HUDStatusBar';
import Ferrofluid from './components/bg/Ferrofluid';
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
    <div className="command-center-root">
      {/* High-End Ferrofluid WebGL Dynamic Background */}
      <div style={{ width: '100%', height: '100%', position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
        <Ferrofluid
          colors={["#ffffff", "#ffffff", "#ffffff"]}
          speed={0.5}
          scale={1.6}
          turbulence={1}
          fluidity={0.1}
          rimWidth={0.2}
          sharpness={2.5}
          shimmer={1.5}
          glow={2}
          flowDirection="down"
          opacity={1}
          mouseInteraction
          mouseStrength={1}
          mouseRadius={0.35}
        />
      </div>

      {/* Main Glass Shell */}
      <div className="command-center-shell">
        {/* Top High-Tech Navigation Bar */}
        <TopNavBar
          activeSessionId={activeSessionId}
          sessionCount={sessions.length}
        />

        {/* Core Workspace Layout */}
        <div className="workspace-grid-container">
          {/* Session Manager Command Sidebar */}
          <SessionSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={handleSelectSession}
            onCreateSession={handleCreateSession}
            onDeleteSession={deleteSession}
            loading={sessionsLoading}
          />

          {/* Interactive Agent Console Viewport */}
          <main className="console-viewport-container">
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
              disabled={!activeSessionId || awaitingConfirmation}
            />
          </main>
        </div>

        {/* Live HUD Status Ribbon */}
        <HUDStatusBar
          activeSessionId={activeSessionId}
          messageCount={messages.length}
        />
      </div>
    </div>
  );
}

export default App;
