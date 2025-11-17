/**
 * Session Manager for Guest Chat
 * Manages session IDs and chat history in localStorage
 */

const SESSION_STORAGE_KEY = 'careagent_guest_session';
const HISTORY_STORAGE_KEY = 'careagent_guest_history';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export class SessionManager {
  private sessionId: string | null = null;

  constructor() {
    this.initSession();
  }

  /**
   * Initialize or retrieve existing session
   */
  private initSession(): void {
    const existingSession = localStorage.getItem(SESSION_STORAGE_KEY);
    if (existingSession) {
      this.sessionId = existingSession;
    } else {
      this.sessionId = this.generateSessionId();
      localStorage.setItem(SESSION_STORAGE_KEY, this.sessionId);
    }
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    return `guest_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Get current session ID
   */
  getSessionId(): string {
    if (!this.sessionId) {
      this.initSession();
    }
    return this.sessionId!;
  }

  /**
   * Get chat history from localStorage
   */
  getHistory(): ChatMessage[] {
    try {
      const history = localStorage.getItem(HISTORY_STORAGE_KEY);
      if (history) {
        return JSON.parse(history);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
    return [];
  }

  /**
   * Save chat history to localStorage
   */
  saveHistory(messages: ChatMessage[]): void {
    try {
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  }

  /**
   * Clear chat history and session
   */
  clearSession(): void {
    localStorage.removeItem(SESSION_STORAGE_KEY);
    localStorage.removeItem(HISTORY_STORAGE_KEY);
    this.sessionId = this.generateSessionId();
    localStorage.setItem(SESSION_STORAGE_KEY, this.sessionId);
  }

  /**
   * Check if this is a new session (no history)
   */
  isNewSession(): boolean {
    const history = this.getHistory();
    return history.length === 0;
  }
}

// Export a singleton instance
export const sessionManager = new SessionManager();
