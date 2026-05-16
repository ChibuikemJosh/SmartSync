import React from 'react';
import { useApp } from '../context/AppContext';

export default function Frame({ children }) {
  const { theme } = useApp();
  const outerBg = theme === 'dark' ? 'bg-[#0b1011] text-white' : 'bg-[#E8ECEE] text-slate-900';
  const innerBg = theme === 'dark' ? 'bg-[#121212]' : 'bg-[#F8F9FA]';

  return (
    <div className={`min-h-screen w-full ${outerBg}`}>
      <div className={`mx-auto min-h-screen max-w-md ${innerBg} shadow-mobile relative overflow-hidden`}>
        <div className="pointer-events-none absolute inset-x-0 top-0 h-44 bg-gradient-to-b from-forest/15 to-transparent" />
        {children}
      </div>
    </div>
  );
}
