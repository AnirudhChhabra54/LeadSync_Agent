import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';

/**
 * Hook for managing chat messages and interactions within a session.
 */
export function useChat(sessionId) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState(null);

  // Load message history whenever active sessionId changes
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setAwaitingConfirmation(false);
      setExtractedData(null);
      setError(null);
      return;
    }

    let isMounted = true;
    setLoading(true);

    api.getSessionMessages(sessionId)
      .then((data) => {
        if (!isMounted) return;
        setMessages(data.messages || []);
        setAwaitingConfirmation(data.status === 'awaiting_confirmation');
        setExtractedData(data.extracted_data || null);
        setError(null);
      })
      .catch((err) => {
        if (!isMounted) return;
        console.warn(`Could not load history for session ${sessionId}:`, err);
        setMessages([]);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  const processResponse = useCallback((data) => {
    if (data.messages && data.messages.length > 0) {
      setMessages(prev => [...prev, ...data.messages]);
    }
    setAwaitingConfirmation(data.status === 'awaiting_confirmation');
    if (data.extracted_data) {
      setExtractedData(data.extracted_data);
    }
    if (data.error) {
      setError(data.error);
    }
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!sessionId || !text.trim()) return;
    setLoading(true);
    setError(null);

    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: text }]);

    try {
      const data = await api.sendMessage(sessionId, text);
      processResponse(data);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }, [sessionId, processResponse]);

  const uploadImage = useCallback(async (file) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);

    // Add user message with image indicator
    setMessages(prev => [...prev, {
      role: 'user',
      content: `📷 Uploaded visiting card: ${file.name}`,
      metadata: { type: 'image_upload', fileName: file.name },
    }]);

    try {
      const data = await api.uploadImage(sessionId, file);
      processResponse(data);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Upload failed: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }, [sessionId, processResponse]);

  const uploadAudio = useCallback(async (file) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);

    setMessages(prev => [...prev, {
      role: 'user',
      content: `🎙️ Uploaded voice note: ${file.name}`,
      metadata: { type: 'audio_upload', fileName: file.name },
    }]);

    try {
      const data = await api.uploadAudio(sessionId, file);
      processResponse(data);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Upload failed: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }, [sessionId, processResponse]);

  const confirmContact = useCallback(async (approved, edits = {}) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);

    setMessages(prev => [...prev, {
      role: 'user',
      content: approved ? '✅ Contact confirmed' : '❌ Contact rejected',
    }]);

    try {
      const data = await api.confirmContact(sessionId, approved, edits);
      processResponse(data);
      setAwaitingConfirmation(false);
      setExtractedData(null);
    } catch (err) {
      setError(err.message);
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }, [sessionId, processResponse]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setAwaitingConfirmation(false);
    setExtractedData(null);
    setError(null);
  }, []);

  return {
    messages,
    loading,
    awaitingConfirmation,
    extractedData,
    error,
    sendMessage,
    uploadImage,
    uploadAudio,
    confirmContact,
    clearChat,
  };
}
