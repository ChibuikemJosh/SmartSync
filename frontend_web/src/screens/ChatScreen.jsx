import React, { useEffect, useRef, useState } from 'react';
import { Mic, SendHorizontal } from 'lucide-react';
import { useApp } from '../context/AppContext';

export default function ChatScreen() {
  const { chatMessages, sendChat, loading } = useApp();
  const [text, setText] = useState('');
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [chatMessages]);

  const handleSend = async () => {
    if (!text.trim()) return;
    const payload = text;
    setText('');
    await sendChat(payload);
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#F8F9FA]">
      <div className="border-b border-slate-200 bg-white px-4 pb-4 pt-4 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-[0.3em] text-forest">AI Advisor</p>
        <h2 className="mt-1 text-2xl font-black text-slate-900">Chat Hub</h2>
      </div>

      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4 scrollbar-hide">
        {chatMessages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[78%] rounded-[22px] px-4 py-3 text-sm leading-6 shadow-md ${message.sender === 'user' ? 'bg-forest text-white' : 'bg-white text-slate-800'}`}>
              {message.text}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-200 bg-white px-3 pb-4 pt-3">
        <div className="flex items-center gap-2 rounded-[26px] bg-[#F8F9FA] p-2 shadow-inner">
          <button
            className="flex h-12 w-12 items-center justify-center rounded-full bg-amber text-slate-900"
            onClick={() => {
              console.log('DEBUG: chat mic tapped');
              window.alert('Mic action vector asset can be wired to recorded voice upload here.');
            }}
          >
            <Mic size={20} />
          </button>
          <input
            className="h-12 flex-1 bg-transparent px-3 text-sm text-slate-900 placeholder:text-slate-400"
            placeholder="Type your message..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="flex h-12 w-12 items-center justify-center rounded-full bg-forest text-white disabled:opacity-70"
          >
            <SendHorizontal size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
