'use client';

import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import type { ChatMessage } from '@/types';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (content: string) => void;
  isLoading: boolean;
}

export function ChatPanel({
  messages,
  onSendMessage,
  isLoading,
}: ChatPanelProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-opal-200 bg-white">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-opal-teal"></div>
          <h2 className="font-semibold text-opal-navy">Chat</h2>
        </div>
        <p className="text-sm text-opal-500 mt-1">
          Describe your research goal to get started
        </p>
      </div>
      <MessageList messages={messages} isLoading={isLoading} />
      <MessageInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
}
