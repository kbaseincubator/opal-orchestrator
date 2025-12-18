'use client';

import { useEffect, useState } from 'react';
import { getConversations, deleteConversation } from '@/lib/api';
import type { ConversationSummary } from '@/types';

interface ChatHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  currentConversationId: string | null;
}

export function ChatHistory({
  isOpen,
  onClose,
  onSelectConversation,
  onNewChat,
  currentConversationId,
}: ChatHistoryProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const data = await getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (deleteConfirm === id) {
      try {
        await deleteConversation(id);
        setConversations((prev) => prev.filter((c) => c.id !== id));
        setDeleteConfirm(null);
        if (currentConversationId === id) {
          onNewChat();
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    } else {
      setDeleteConfirm(id);
      // Reset after 3 seconds
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-40"
          onClick={onClose}
        />
      )}

      {/* Slide-out panel */}
      <div
        className={`fixed left-0 top-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-opal-200 bg-opal-navy text-white">
          <h2 className="font-semibold">Chat History</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-opal-navy-light rounded transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* New Chat button */}
        <div className="p-4 border-b border-opal-200">
          <button
            onClick={() => {
              onNewChat();
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-opal-teal text-white rounded-lg hover:bg-opal-teal-dark transition-colors font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Conversations list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="flex items-center gap-2 text-opal-500">
                <div className="w-2 h-2 bg-opal-teal rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-opal-purple rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-opal-magenta rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-opal-500">
              <svg className="w-12 h-12 mx-auto mb-3 text-opal-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-sm">No conversations yet</p>
              <p className="text-xs mt-1">Start a new chat to begin</p>
            </div>
          ) : (
            <div className="divide-y divide-opal-100">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => {
                    onSelectConversation(conv.id);
                    onClose();
                  }}
                  className={`p-4 cursor-pointer hover:bg-opal-50 transition-colors ${
                    currentConversationId === conv.id ? 'bg-opal-100 border-l-4 border-opal-teal' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-opal-navy text-sm truncate">
                        {conv.title || 'Untitled conversation'}
                      </h3>
                      <p className="text-xs text-opal-500 mt-1 line-clamp-2">
                        {conv.preview}
                      </p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-opal-400">
                        <span>{formatDate(conv.updated_at)}</span>
                        <span>{conv.message_count} messages</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => handleDelete(conv.id, e)}
                      className={`p-1.5 rounded transition-colors flex-shrink-0 ${
                        deleteConfirm === conv.id
                          ? 'bg-opal-magenta text-white'
                          : 'text-opal-400 hover:text-opal-magenta hover:bg-opal-100'
                      }`}
                      title={deleteConfirm === conv.id ? 'Click again to confirm' : 'Delete conversation'}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-opal-200 bg-opal-50 text-center text-xs text-opal-500">
          {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
        </div>
      </div>
    </>
  );
}
