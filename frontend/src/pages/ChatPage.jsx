import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send } from 'lucide-react';
import client from '../api/client';
import { cn } from '../lib/utils';

const ChatPage = ({ metrics, filename, chatMessages, setChatMessages }) => {
    const [chatInput, setChatInput] = useState('');
    // Local state removed (lifted to App.jsx)
    const [isChatLoading, setIsChatLoading] = useState(false);
    const chatEndRef = useRef(null);

    const scrollToBottom = () => chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    useEffect(scrollToBottom, [chatMessages]);

    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput.trim()) return;

        const msg = chatInput;
        setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
        setChatInput('');
        setIsChatLoading(true);

        try {
            const context = `Total: ${metrics?.total}, High Prio: ${metrics?.high}`;
            const res = await client.post(`/chat`, {
                message: msg,
                context,
                filename: filename
            });
            setChatMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
        } catch (err) {
            setChatMessages(prev => [...prev, { role: 'assistant', content: "Connection error. Please try again." }]);
        } finally {
            setIsChatLoading(false);
        }
    };

    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mx-auto max-w-4xl">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600">
                    <Bot size={20} />
                </div>
                <div>
                    <h3 className="font-bold text-slate-800">AI Data Assistant</h3>
                    <p className="text-xs text-slate-500">Ask questions about your data</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
                {chatMessages.map((msg, idx) => (
                    <div key={idx} className={cn(
                        "flex w-full",
                        msg.role === 'user' ? "justify-end" : "justify-start"
                    )}>
                        <div className={cn(
                            "max-w-[80%] rounded-2xl px-5 py-3.5 text-sm shadow-sm",
                            msg.role === 'user'
                                ? "bg-primary-600 text-white rounded-br-none"
                                : "bg-white border border-slate-200 text-slate-700 rounded-bl-none"
                        )}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isChatLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 shadow-sm flex gap-1">
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-75" />
                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150" />
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-slate-200">
                <form onSubmit={handleChatSubmit} className="relative">
                    <input
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        placeholder="Type your question..."
                        className="w-full bg-slate-100 border-none rounded-xl pl-4 pr-12 py-3.5 text-sm focus:ring-2 focus:ring-primary-500 transition-all"
                    />
                    <button
                        type="submit"
                        disabled={!chatInput.trim()}
                        className="absolute right-2 top-2 p-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatPage;
