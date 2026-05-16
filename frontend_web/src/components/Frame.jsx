import React from 'react';

export default function Frame({ children }) {
  return (
    <div className="min-h-screen w-full bg-[#E8ECEE] text-slate-900">
      <div className="mx-auto min-h-screen max-w-md bg-[#F8F9FA] shadow-mobile relative overflow-hidden">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-44 bg-gradient-to-b from-forest/15 to-transparent" />
        {children}
      </div>
    </div>
  );
}
