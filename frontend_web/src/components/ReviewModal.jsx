import React from 'react';
import { X } from 'lucide-react';
import LoadingButton from './LoadingButton';

export default function ReviewModal({ open, transaction, onClose, onChange, onConfirm, loading }) {
  if (!open || !transaction) return null;

  return (
    <div className="absolute inset-0 z-40 flex items-end bg-slate-950/55 backdrop-blur-sm">
      <div className="w-full rounded-t-[30px] bg-[#F8F9FA] p-5 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-forest">AI Review</p>
            <h3 className="text-xl font-extrabold text-slate-900">Confirm Transaction</h3>
          </div>
          <button onClick={onClose} className="rounded-full bg-slate-100 p-2 text-slate-600">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-4">
          <label className="block">
            <span className="mb-2 block text-sm font-semibold text-slate-700">Item Name</span>
            <input
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
              value={transaction.item}
              onChange={(e) => onChange('item', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-semibold text-slate-700">Price</span>
            <input
              type="number"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
              value={transaction.amount}
              onChange={(e) => onChange('amount', e.target.value)}
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-semibold text-slate-700">Quantity</span>
            <input
              type="number"
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
              value={transaction.quantity}
              onChange={(e) => onChange('quantity', e.target.value)}
            />
          </label>
          <LoadingButton
            isLoading={loading}
            className="w-full bg-amber text-slate-900 shadow-lg shadow-amber/20"
            onClick={onConfirm}
          >
            Confirm & Log to Graph Ledger
          </LoadingButton>
        </div>
      </div>
    </div>
  );
}
