import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';
import { Send, Bot, User, Sparkles } from 'lucide-react';

const suggestedPrompts = [
  "Are there any civic improvements today?",
  "Which communities need support right now?",
  "What is the momentum like in Salt Lake?"
];

const Chat = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello. I am the Owe Civic AI. I can help you understand recent community momentum, active friction points, and ways to support your neighbors.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text) => {
    if (!text.trim()) return;
    
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(text);
      setMessages(prev => [...prev, { role: 'assistant', content: response.reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I am temporarily having difficulty reaching the local civic records. Please try asking again in a few moments, or check back shortly.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col animate-in fade-in duration-700 max-w-4xl mx-auto pb-8">
      
      <div className="mb-8 text-center space-y-3">
        <h2 className="text-3xl font-semibold tracking-tight text-slate-900 flex items-center justify-center">
          <Sparkles size={24} className="text-teal-600 mr-2" />
          Conversational Civic Intelligence
        </h2>
        <p className="text-slate-500 text-lg">Explore local momentum, analyze friction, and find ways to help.</p>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-white rounded-2xl border border-slate-100 shadow-sm mb-6 custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex items-start space-x-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center flex-shrink-0 border border-teal-100 shadow-sm">
                <Bot size={20} />
              </div>
            )}
            <div className={`max-w-[75%] rounded-2xl px-5 py-4 text-base leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-slate-900 text-white rounded-tr-sm shadow-sm' 
                : msg.content.includes('difficulty') 
                  ? 'bg-rose-50/50 text-rose-800 border border-rose-100 rounded-tl-sm' 
                  : 'bg-slate-50 text-slate-700 border border-slate-100 rounded-tl-sm'
            }`}>
              {msg.content.split('\n').map((line, i) => (
                <span key={i}>
                  {line}
                  <br/>
                </span>
              ))}
            </div>
            {msg.role === 'user' && (
              <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-500 flex items-center justify-center flex-shrink-0 border border-slate-200">
                <User size={20} />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start space-x-4 justify-start">
            <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center flex-shrink-0 border border-teal-100">
              <Bot size={20} />
            </div>
            <div className="bg-slate-50 text-slate-500 border border-slate-100 px-5 py-4 rounded-2xl rounded-tl-sm flex space-x-1.5 items-center">
              <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      {messages.length === 1 && (
        <div className="flex flex-wrap gap-3 mb-6 justify-center">
          {suggestedPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="text-sm bg-white hover:bg-teal-50 hover:text-teal-700 text-slate-600 px-4 py-2 rounded-full transition-colors border border-slate-200 hover:border-teal-200 shadow-sm"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Ask about neighborhood momentum or challenges..."
          className="w-full bg-white border border-slate-200 rounded-2xl py-5 pl-6 pr-16 shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-base placeholder:text-slate-400"
        />
        <button
          onClick={() => handleSend(input)}
          disabled={!input.trim() || isLoading}
          className="absolute right-3 top-3 bottom-3 w-12 bg-slate-900 hover:bg-teal-600 text-white rounded-xl flex items-center justify-center disabled:opacity-50 transition-colors shadow-sm"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default Chat;
