import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export default function StatCard({ title, value, icon, subtitle, trend }: StatCardProps) {
  return (
    <div className="relative group rounded-2xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
      {/* Animated gradient border */}
      <div className="absolute inset-0 bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 group-hover:from-primary/50 group-hover:via-primary/30 group-hover:to-primary/50 opacity-50 transition-all duration-500"></div>
      
      {/* Glass content container */}
      <div className="relative m-[1px] bg-surface/90 backdrop-blur-xl p-6 rounded-2xl h-[calc(100%-2px)] border border-white/5 flex flex-col justify-between overflow-hidden">
        
        {/* Glow effect */}
        <div className="absolute -top-10 -right-10 w-40 h-40 bg-primary/10 rounded-full blur-3xl group-hover:bg-primary/20 transition-all duration-700 pointer-events-none"></div>

        <div className="flex justify-between items-start z-10 relative">
          <div>
            <p className="text-gray-400 text-xs font-bold uppercase tracking-widest">{title}</p>
            <h3 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-gray-400 mt-2 tracking-tight">
              {value}
            </h3>
            
            {subtitle && (
              <p className={`text-xs mt-3 font-semibold px-2 py-1 inline-flex rounded-full bg-black/40 border border-white/5 ${
                trend === 'up' ? 'text-green-400 shadow-[0_0_10px_rgba(74,222,128,0.2)]' : trend === 'down' ? 'text-red-400 shadow-[0_0_10px_rgba(248,113,113,0.2)]' : 'text-gray-400'
              }`}>
                {subtitle}
              </p>
            )}
          </div>
          
          {icon && (
            <div className="p-3.5 bg-gradient-to-br from-gray-800 to-black rounded-xl text-primary shadow-[0_4px_15px_rgba(212,175,55,0.15)] border border-primary/20 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
