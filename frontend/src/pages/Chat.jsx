import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

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
    <div className="h-[calc(100vh-13rem)] md:h-[600px] flex flex-col animate-page-transition max-w-3xl mx-auto pb-4">
      
      <div className="mb-4 text-center space-y-2 bg-glow-glow py-3 rounded-2xl relative overflow-hidden">
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-owe-textPrimary flex items-center justify-center relative z-10">
          <Sparkles size={20} className="text-owe-primary mr-2" />
          Conversational Civic AI
        </h2>
        <p className="text-owe-textSecondary text-sm sm:text-base relative z-10">Explore local momentum, analyze friction, and find ways to help.</p>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-white rounded-2xl border border-owe-border/80 shadow-soft mb-4 custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-2">
            <div className={`flex items-start space-x-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-owe-primary to-owe-secondary text-white flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Bot size={16} />
                </div>
              )}
              <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm sm:text-base leading-relaxed break-words overflow-hidden ${
                msg.role === 'user' 
                  ? 'bg-owe-primary text-white rounded-tr-sm shadow-sm font-medium' 
                  : msg.content.includes('difficulty') 
                    ? 'bg-rose-50/75 text-owe-danger border border-rose-100 rounded-tl-sm' 
                    : 'bg-owe-cyan/15 text-owe-textPrimary border border-owe-border/40 rounded-tl-sm'
              }`}>
                {msg.role === 'user' ? (
                  msg.content.split('\n').map((line, i) => (
                    <span key={i}>
                      {line}
                      {i < msg.content.split('\n').length - 1 && <br/>}
                    </span>
                  ))
                ) : (
                  <ReactMarkdown
                    components={{
                      p: ({ node, ...props }) => <p className="mb-2 last:mb-0 leading-relaxed text-sm sm:text-base text-inherit" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-2 space-y-1 text-sm sm:text-base text-inherit" {...props} />,
                      ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-2 space-y-1 text-sm sm:text-base text-inherit" {...props} />,
                      li: ({ node, ...props }) => <li className="text-sm sm:text-base text-inherit" {...props} />,
                      strong: ({ node, ...props }) => <strong className="font-bold text-inherit" {...props} />,
                      em: ({ node, ...props }) => <em className="italic text-inherit" {...props} />,
                      h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-1 mt-2 text-inherit" {...props} />,
                      h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-1 mt-2 text-inherit" {...props} />,
                      h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-1 mt-1 text-inherit" {...props} />,
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-owe-bg text-owe-textSecondary flex items-center justify-center flex-shrink-0 border border-owe-border">
                  <User size={16} />
                </div>
              )}
            </div>
            
            {/* Quick Suggestions below the latest assistant response */}
            {msg.role === 'assistant' && idx === messages.length - 1 && !isLoading && (
              <div className="pl-11 flex flex-wrap gap-2 pt-1 animate-in fade-in duration-300">
                {suggestedPrompts.map((prompt, pIdx) => (
                  <button
                    key={pIdx}
                    onClick={() => handleSend(prompt)}
                    className="text-xs bg-owe-cyan/35 hover:bg-owe-primary hover:text-white text-owe-primary px-3 py-1.5 rounded-full border border-owe-border/60 hover:border-owe-primary transition-all duration-200 font-semibold focus:outline-none"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start space-x-3 justify-start">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-owe-primary to-owe-secondary text-white flex items-center justify-center flex-shrink-0 shadow-sm">
              <Bot size={16} />
            </div>
            <div className="bg-owe-cyan/15 text-owe-textSecondary border border-owe-border/45 px-4 py-2.5 rounded-2xl rounded-tl-sm flex space-x-1.5 items-center">
              <div className="w-1.5 h-1.5 rounded-full bg-owe-primary/70 animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-1.5 h-1.5 rounded-full bg-owe-primary/70 animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-1.5 h-1.5 rounded-full bg-owe-primary/70 animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="relative mt-1">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
          placeholder="Ask about neighborhood momentum or challenges..."
          className="w-full bg-white border border-owe-border rounded-xl py-3.5 pl-4 pr-14 shadow-soft focus:outline-none focus:ring-2 focus:ring-owe-primary/10 focus:border-owe-primary transition-all text-sm sm:text-base placeholder:text-owe-textMuted text-owe-textPrimary"
        />
        <button
          onClick={() => handleSend(input)}
          disabled={!input.trim() || isLoading}
          className="absolute right-2 top-2 bottom-2 w-10 bg-owe-primary hover:bg-owe-secondary text-white rounded-lg flex items-center justify-center disabled:opacity-50 transition-all duration-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-owe-primary/20"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default Chat;
