'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChatPanel } from '@/components/Chat/ChatPanel';
import { ChatHistory } from '@/components/Chat/ChatHistory';
import { PlanPanel } from '@/components/Plan/PlanPanel';
import { SourcesPanel } from '@/components/Sources/SourcesPanel';
import type { ChatMessage, OPALPlan, SearchResult } from '@/types';
import { sendChatMessage, waitForChatJob, getConversation } from '@/lib/api';

const WELCOME_MESSAGE: ChatMessage = {
  role: 'assistant',
  content: `Welcome to the **OPAL Orchestrator**! I'm here to help you plan cross-lab biological research projects across the OPAL network.

Tell me about your research goal, and I'll help you:
- Identify relevant OPAL capabilities and facilities
- Create a sequenced research plan with citations
- Find the fastest path to actionable insights

**Example:** "I want to develop a drought-tolerant microbial strain that produces plant growth hormones and can associate with plant roots."

What research goal would you like to explore?`,
};

function ChatPageContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [initialGoalProcessed, setInitialGoalProcessed] = useState(false);
  const [currentPlan, setCurrentPlan] = useState<OPALPlan | null>(null);
  const [sources, setSources] = useState<SearchResult[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const handleSendMessage = useCallback(async (content: string) => {
    // Add user message
    const userMessage: ChatMessage = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Submit chat job - returns immediately with job_id
      const submitResponse = await sendChatMessage({
        message: content,
        conversation_id: conversationId || undefined,
      });

      // Wait for job to complete with progress tracking
      const response = await waitForChatJob(submitResponse.job_id, {
        onProgress: (job) => {
          // Could show progress indicator here if needed
          console.log(`Job ${submitResponse.job_id} progress:`, job.progress);
        },
      });

      // Update conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant message
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Update plan if present
      if (response.plan) {
        setCurrentPlan(response.plan);
      }

      // Update sources
      if (response.sources && response.sources.length > 0) {
        setSources((prev) => {
          // Deduplicate sources
          const existing = new Set(prev.map((s) => s.chunk_id));
          const newSources = response.sources.filter(
            (s) => !existing.has(s.chunk_id)
          );
          return [...prev, ...newSources];
        });
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      let errorContent: string = error?.message;
      if (!errorContent) {
        errorContent = 'Sorry, I encountered an error processing your request. Please try again.';
      }
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: errorContent,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  // Handle initial goal from URL query parameter
  useEffect(() => {
    const goal = searchParams.get('goal');
    if (goal && !initialGoalProcessed) {
      setInitialGoalProcessed(true);
      // Automatically send the goal as first message
      handleSendMessage(goal);
    }
  }, [searchParams, initialGoalProcessed, handleSendMessage]);

  const handleNewChat = () => {
    setMessages([WELCOME_MESSAGE]);
    setCurrentPlan(null);
    setSources([]);
    setConversationId(null);
    setInitialGoalProcessed(false);
  };

  const handleSelectConversation = async (id: string) => {
    try {
      setIsLoading(true);
      const conversation = await getConversation(id);

      // Convert messages to ChatMessage format
      const loadedMessages: ChatMessage[] = conversation.messages.map((msg) => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
      }));

      setMessages(loadedMessages.length > 0 ? loadedMessages : [WELCOME_MESSAGE]);
      setCurrentPlan(conversation.plan);
      setConversationId(id);
      // Load persisted sources
      setSources(conversation.sources || []);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Chat History Slide-out */}
      <ChatHistory
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        currentConversationId={conversationId}
      />

      <div className="h-[calc(100vh-64px)] flex">
        {/* Chat Panel - Left */}
        <div className="w-1/3 min-w-[400px] border-r border-opal-200 flex flex-col bg-white">
          {/* History button bar */}
          <div className="px-4 py-2 border-b border-opal-100 bg-opal-50 flex items-center gap-2">
            <button
              onClick={() => setIsHistoryOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-opal-600 hover:text-opal-navy hover:bg-white rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              History
            </button>
            <button
              onClick={handleNewChat}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-opal-600 hover:text-opal-navy hover:bg-white rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Chat
            </button>
            {conversationId && (
              <span className="ml-auto text-xs text-opal-400 truncate max-w-[150px]" title={conversationId}>
                ID: {conversationId.slice(0, 8)}...
              </span>
            )}
          </div>
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>

        {/* Plan Panel - Center */}
        <div className="w-1/3 min-w-[400px] border-r border-opal-200 flex flex-col bg-opal-50">
          <PlanPanel plan={currentPlan} />
        </div>

        {/* Sources Panel - Right */}
        <div className="w-1/3 min-w-[350px] flex flex-col bg-white">
          <SourcesPanel sources={sources} />
        </div>
      </div>
    </>
  );
}

// Loading fallback for Suspense
function ChatPageLoading() {
  return (
    <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-opal-50">
      <div className="flex items-center gap-3 text-opal-500">
        <div className="w-2 h-2 bg-opal-teal rounded-full animate-bounce" />
        <div className="w-2 h-2 bg-opal-purple rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
        <div className="w-2 h-2 bg-opal-magenta rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        <span>Loading chat...</span>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<ChatPageLoading />}>
      <ChatPageContent />
    </Suspense>
  );
}
