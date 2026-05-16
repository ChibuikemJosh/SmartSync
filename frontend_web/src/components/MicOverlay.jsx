import React from 'react';
import { Mic, X } from 'lucide-react';

export default function MicOverlay({ open, onClose, onPickVoice }) {
  if (!open) return null;

  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center bg-slate-950/55 px-5 backdrop-blur-sm">
      <div className="w-full max-w-sm rounded-[28px] bg-white p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-forest">Voice Capture</p>
            <h3 className="text-xl font-extrabold text-slate-900">Speak Record</h3>
          </div>
          <button onClick={onClose} className="rounded-full bg-slate-100 p-2 text-slate-600">
            <X size={18} />
          </button>
        </div>
        <div className="mx-auto flex h-32 w-32 items-center justify-center rounded-full bg-forest/10">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-forest text-white shadow-lg shadow-forest/30">
            <Mic size={32} />
          </div>
        </div>
        <p className="mt-4 text-center text-sm leading-6 text-slate-600">
          Upload a voice note and the AI status polling will guide you into the review screen.
        </p>
        <label className="mt-4 block cursor-pointer rounded-2xl bg-forest px-4 py-3 text-center font-semibold text-white">
          Choose Voice File
          <input
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onPickVoice(file);
            }}
          />
        </label>
      </div>
    </div>
  );
}
