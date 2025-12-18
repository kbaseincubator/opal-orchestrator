'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';

interface MessageInputProps {
  onSend: (content: string) => void;
  disabled: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4 border-t border-opal-200 bg-white">
      <div className="flex gap-2">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your research goal..."
          disabled={disabled}
          className="flex-1 resize-none rounded-lg border border-opal-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-opal-teal focus:border-transparent disabled:bg-opal-100 disabled:cursor-not-allowed text-opal-800 placeholder-opal-400"
          rows={1}
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className="px-6 py-3 bg-opal-navy text-white rounded-lg hover:bg-opal-navy-light transition-colors disabled:bg-opal-300 disabled:cursor-not-allowed font-medium shadow-sm"
        >
          Send
        </button>
      </div>
      <p className="text-xs text-opal-400 mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
