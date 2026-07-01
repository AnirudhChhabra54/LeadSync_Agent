export default function MessageBubble({ message }) {
  const role = message.role || 'assistant';

  // Simple markdown-like rendering for bold text
  const renderContent = (text) => {
    if (!text) return null;

    // Split by **bold** markers
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      // Handle newlines
      return part.split('\n').map((line, j) => (
        <span key={`${i}-${j}`}>
          {j > 0 && <br />}
          {line}
        </span>
      ));
    });
  };

  return (
    <div className={`message-bubble ${role}`}>
      {renderContent(message.content)}
    </div>
  );
}
