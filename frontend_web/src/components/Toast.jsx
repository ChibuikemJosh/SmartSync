import React from 'react';

const toneStyles = {
  forest: 'bg-forest text-white',
  amber: 'bg-amber text-slate-900',
};

export default function Toast({ toast }) {
  if (!toast) return null;

  return (
    <div className="absolute left-1/2 top-4 z-50 w-[92%] -translate-x-1/2 rounded-2xl px-4 py-3 shadow-2xl">
      <div className={`rounded-2xl px-4 py-3 text-sm font-semibold ${toneStyles[toast.tone] || toneStyles.forest}`}>
        {toast.message}
      </div>
    </div>
  );
}
