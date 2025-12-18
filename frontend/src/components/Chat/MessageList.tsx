'use client';

import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '@/types';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-opal-50">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-[85%] rounded-lg px-4 py-3 shadow-sm ${
              message.role === 'user'
                ? 'bg-opal-navy text-white'
                : 'bg-white border border-opal-200 text-opal-800'
            }`}
          >
            {message.role === 'assistant' ? (
              <div className="markdown-content prose prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            ) : (
              <p className="whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white border border-opal-200 rounded-lg px-4 py-3 shadow-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-opal-teal rounded-full animate-bounce" />
              <div
                className="w-2 h-2 bg-opal-purple rounded-full animate-bounce"
                style={{ animationDelay: '0.1s' }}
              />
              <div
                className="w-2 h-2 bg-opal-magenta rounded-full animate-bounce"
                style={{ animationDelay: '0.2s' }}
              />
              <span className="text-sm text-opal-500 ml-2">Thinking...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
