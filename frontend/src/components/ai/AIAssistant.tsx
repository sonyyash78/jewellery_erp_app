import { useState, useRef, useEffect } from 'react';
import { axiosClient } from '../../api/axiosClient';
import {
  Bot,
  X,
  Send,
  Sparkles,
  RotateCcw,
  Maximize2,
  Minimize2,
  Copy,
  Check,
  TrendingUp,
  Scale,
  Users,
  Coins,
  Receipt,
  Repeat,
  Wallet,
  Truck
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  text: string;
  timestamp: string;
}

const INITIAL_GREETING: ChatMessage = {
  id: 'init-1',
  role: 'ai',
  text: '🙏 **Namaste! Main aapka Saideep Jewellery ERP Assistant hoon.**\n\nAap mujhse store ke business ke baare me Hindi, Hinglish ya English me pooch sakte hain. Niche diye buttons par click karein ya apna sawal type karein!',
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
};

interface QuickPrompt {
  id: string;
  label: string;
  query: string;
  icon: typeof TrendingUp;
  color: string;
}

const QUICK_PROMPTS: QuickPrompt[] = [
  { id: 'sales', label: 'Aaj Ki Sale', query: 'Aaj ki sale kitni hui?', icon: TrendingUp, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  { id: 'stock', label: 'Gold & Silver Stock', query: 'Gold aur silver stock kitna hai?', icon: Scale, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  { id: 'udhari', label: 'Udhari (Dues)', query: 'Kiske paise baaki hain? Top udhari dikhao', icon: Users, color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  { id: 'rates', label: 'Live Metal Rates', query: 'Aaj ka gold aur silver rate kya hai?', icon: Coins, color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' },
  { id: 'bills', label: 'Aaj Ke Bills', query: 'Aaj kitne bill bane?', icon: Receipt, color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  { id: 'exchange', label: 'Purana Sona (Exchange)', query: 'Purana sona kitna aaya (Exchange summary)?', icon: Repeat, color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  { id: 'kharcha', label: 'Dukan Ka Kharcha', query: 'Aaj ka kharcha kitna hua?', icon: Wallet, color: 'text-orange-400 bg-orange-500/10 border-orange-500/20' },
  { id: 'supplier', label: 'Karigar / Supplier Dues', query: 'Supplier ko kitne paise dene hain?', icon: Truck, color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
];

export default function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading, isOpen]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const [isGeminiActive, setIsGeminiActive] = useState(false);

  const handleSend = async (textToSend?: string) => {
    const queryText = (textToSend !== undefined ? textToSend : input).trim();
    if (!queryText || isLoading) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const historyPayload = messages.slice(-8).map(m => ({
        role: m.role,
        text: m.text
      }));

      const res = await axiosClient.post('/ai/chat', {
        prompt: queryText,
        history: historyPayload
      });

      if (res.data?.source === 'gemini') {
        setIsGeminiActive(true);
      }

      const aiReply = res.data?.response || 'Koi jankari nahi mili.';
      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'ai',
        text: aiReply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'ai',
        text: '⚠️ Maaf kijiye, server se connect karne me dikkat aa rahi hai. Kripya thodi der baad prayas karein.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetChat = () => {
    setMessages([{
      ...INITIAL_GREETING,
      id: `init-${Date.now()}`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }]);
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId(null);
    }, 2000);
  };

  return (
    <div className="fixed bottom-3 right-3 sm:bottom-6 sm:right-6 z-50 font-sans">
      {/* Floating Action Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="relative group bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600 text-black p-3.5 sm:p-4 rounded-full shadow-2xl shadow-amber-500/30 transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center border-2 border-amber-300/60"
          title="Open Jewellery AI Assistant"
        >
          <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
          <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-zinc-950 rounded-full" />
          <span className="sr-only">Open ERP AI Assistant</span>
          <span className="hidden group-hover:block absolute right-full mr-3 whitespace-nowrap bg-zinc-900 border border-zinc-700 text-amber-300 text-xs px-3 py-1.5 rounded-lg shadow-xl font-medium">
            AI Assistant Se Poochein ✨
          </span>
        </button>
      )}

      {/* Main Chat Panel */}
      {isOpen && (
        <div
          className={`bg-zinc-950/95 backdrop-blur-xl border border-zinc-800 shadow-2xl rounded-2xl flex flex-col overflow-hidden transition-all duration-300 ${
            isExpanded
              ? 'w-[720px] max-w-[calc(100vw-1.5rem)] h-[760px] max-h-[calc(100vh-2rem)]'
              : 'w-[410px] max-w-[calc(100vw-1.5rem)] h-[540px] sm:h-[580px] max-h-[calc(100vh-2rem)]'
          }`}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-zinc-950 via-zinc-900 to-zinc-950 p-3.5 border-b border-zinc-800 flex justify-between items-center select-none">
            <div className="flex items-center gap-3">
              <div className="relative bg-gradient-to-br from-amber-400 to-amber-600 text-black p-2 rounded-xl shadow-md shadow-amber-500/20">
                <Bot className="w-5 h-5" />
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-zinc-950 rounded-full" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-zinc-100 text-sm tracking-wide">
                    {isGeminiActive ? 'Gemini AI Copilot' : 'Saideep AI Copilot'}
                  </h3>
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded border ${
                    isGeminiActive
                      ? 'bg-purple-500/20 text-purple-300 border-purple-500/40 shadow-sm shadow-purple-500/20'
                      : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                  }`}>
                    {isGeminiActive ? '✨ Gemini AI' : 'Bilingual AI'}
                  </span>
                </div>
                <p className="text-xs text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping" />
                  Online &middot; Sona, Chandi, Bikri & Udhari
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1 text-zinc-400">
              <button
                onClick={handleResetChat}
                className="p-1.5 hover:text-amber-400 hover:bg-zinc-800/80 rounded-lg transition-colors"
                title="Clear conversation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 hover:text-amber-400 hover:bg-zinc-800/80 rounded-lg transition-colors hidden sm:block"
                title={isExpanded ? 'Shrink' : 'Expand window'}
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:text-rose-400 hover:bg-zinc-800/80 rounded-lg transition-colors ml-1"
                title="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Area */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-zinc-950/70">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`group relative max-w-[88%] rounded-2xl p-3.5 text-sm transition-all ${
                    m.role === 'user'
                      ? 'bg-gradient-to-r from-amber-400 to-amber-500 text-black font-medium rounded-tr-xs shadow-md shadow-amber-500/10'
                      : 'bg-zinc-900 border border-zinc-800/90 text-zinc-200 rounded-tl-xs shadow-md'
                  }`}
                >
                  <ReactMarkdown
                    components={{
                      strong: ({ children }) => (
                        <strong className={m.role === 'user' ? 'font-bold text-black' : 'font-semibold text-amber-300'}>
                          {children}
                        </strong>
                      ),
                      p: ({ children }) => (
                        <p className={`mb-2 last:mb-0 leading-relaxed ${m.role === 'user' ? 'text-zinc-950' : 'text-zinc-200'}`}>
                          {children}
                        </p>
                      ),
                      ul: ({ children }) => (
                        <ul className="list-disc pl-4 space-y-1 my-2 text-zinc-300">
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal pl-4 space-y-1 my-2 text-zinc-300">
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li className="leading-snug">
                          {children}
                        </li>
                      ),
                      code: ({ children }) => (
                        <code className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                          m.role === 'user' ? 'bg-amber-600/40 text-black font-semibold' : 'bg-zinc-800 text-amber-300'
                        }`}>
                          {children}
                        </code>
                      )
                    }}
                  >
                    {m.text}
                  </ReactMarkdown>

                  {/* Copy Button for AI messages */}
                  {m.role === 'ai' && (
                    <button
                      onClick={() => handleCopy(m.id, m.text)}
                      className="absolute -top-2.5 right-2 opacity-0 group-hover:opacity-100 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-amber-300 border border-zinc-700 rounded-md px-1.5 py-0.5 text-[10px] flex items-center gap-1 shadow-md transition-all"
                      title="Copy response (WhatsApp ready)"
                    >
                      {copiedId === m.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  )}
                </div>

                <span className="text-[10px] text-zinc-500 mt-1 px-1">
                  {m.timestamp}
                </span>
              </div>
            ))}

            {/* Loading Skeleton */}
            {isLoading && (
              <div className="flex flex-col items-start">
                <div className="bg-zinc-900 border border-zinc-800 text-zinc-400 rounded-2xl rounded-tl-xs p-3.5 shadow-md flex items-center gap-2">
                  <span className="text-xs text-amber-400/90 font-medium">ERP data check ho raha hai...</span>
                  <div className="flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Action Pills (Horizontal scroll) */}
          <div className="px-3 py-2 border-t border-zinc-800/80 bg-zinc-900/60 overflow-x-auto no-scrollbar flex items-center gap-1.5">
            {QUICK_PROMPTS.map((p) => {
              const IconComp = p.icon;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSend(p.query)}
                  disabled={isLoading}
                  className={`flex-shrink-0 flex items-center gap-1.5 border text-xs px-2.5 py-1 rounded-full transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 ${p.color}`}
                >
                  <IconComp className="w-3 h-3" />
                  <span>{p.label}</span>
                </button>
              );
            })}
          </div>

          {/* Input Area */}
          <div className="p-3 bg-zinc-950 border-t border-zinc-800">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Poochiye: Aaj ki sale, stock, udhari, rates..."
                disabled={isLoading}
                className="flex-1 bg-zinc-900 border border-zinc-800 focus:border-amber-400 rounded-xl px-3.5 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition-colors"
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 disabled:opacity-40 disabled:hover:from-amber-400 disabled:hover:to-amber-500 text-black p-2.5 rounded-xl transition-all font-semibold flex items-center justify-center shadow-md shadow-amber-500/10 active:scale-95"
                title="Send query"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
