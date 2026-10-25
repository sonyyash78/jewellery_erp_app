import { Sparkles } from 'lucide-react';

export default function AiAssistantCard() {
  return (
    <div className="bg-gradient-to-br from-surface to-background rounded-xl border border-primary/30 p-6 relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <Sparkles size={120} className="text-primary" />
      </div>
      
      <div className="relative z-10 flex flex-col h-full">
        <div className="flex items-center space-x-2 mb-2">
          <Sparkles size={20} className="text-primary" />
          <h3 className="font-bold text-lg text-primary">ERP AI Assistant</h3>
        </div>
        
        <p className="text-sm text-textMuted mb-6 flex-1">
          Ask me to analyze sales trends, find a specific customer, or generate an inventory restock report.
        </p>
        
        <div className="relative">
          <input 
            type="text" 
            placeholder="Ask AI..." 
            className="w-full bg-background/50 border border-gray-700 rounded-full px-4 py-2.5 text-sm text-textMain focus:outline-none focus:border-primary placeholder-gray-500 backdrop-blur-sm"
          />
          <button className="absolute right-1 top-1 bottom-1 bg-primary text-black font-medium px-4 rounded-full text-xs hover:bg-primary-dark transition-colors">
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}
