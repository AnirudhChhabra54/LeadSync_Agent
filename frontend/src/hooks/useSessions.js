import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';

/**
 * Hook for managing chat sessions.
 */
export function useSessions() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    try {
      const data = await api.listSessions();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error('Failed to fetch sessions:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createSession = useCallback(async () => {
    try {
      const data = await api.createSession();
      setSessions(prev => [
        { ...data, message_count: 0, has_pending_contact: false, updated_at: data.created_at },
        ...prev,
      ]);
      setActiveSessionId(data.session_id);
      return data.session_id;
    } catch (err) {
      console.error('Failed to create session:', err);
      return null;
    }
  }, []);

  const deleteSession = useCallback(async (sessionId) => {
    try {
      await api.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  }, [activeSessionId]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return {
    sessions,
    activeSessionId,
    setActiveSessionId,
    createSession,
    deleteSession,
    loading,
    refreshSessions: fetchSessions,
  };
}
