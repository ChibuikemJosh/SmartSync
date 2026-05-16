import React from 'react';
import LoadingButton from '../components/LoadingButton';
import { useApp } from '../context/AppContext';

export default function WalletScreen() {
  const { wallet, createVirtualAccount, withdraw, withdrawForm, setWithdrawForm, loading } = useApp();

  const banks = [
    { name: 'GTBank', code: '058' },
    { name: 'Access Bank', code: '044' },
    { name: 'Zenith Bank', code: '057' },
    { name: 'First Bank', code: '011' },
  ];

  return (
    <div className="min-h-screen px-4 pb-6 pt-4">
      <p className="text-xs font-bold uppercase tracking-[0.3em] text-forest">Financial Toolkit</p>
      <h2 className="mt-2 text-3xl font-black text-slate-900">Wallet</h2>

      <div className="mt-5 rounded-[28px] bg-gradient-to-br from-forest to-[#0a3e44] p-5 text-white shadow-2xl">
        <p className="text-xs uppercase tracking-[0.25em] text-white/70">Virtual Account</p>
        <h3 className="mt-2 text-2xl font-black">{wallet.merchantTitle || 'Merchant Title'}</h3>
        <div className="mt-5 grid grid-cols-1 gap-3 text-sm">
          <div className="rounded-2xl bg-white/10 p-4">
            <p className="text-xs text-white/60">Account Number</p>
            <p className="mt-1 text-lg font-extrabold">{wallet.accountNumber || 'Pending creation'}</p>
          </div>
          <div className="rounded-2xl bg-white/10 p-4">
            <p className="text-xs text-white/60">Bank Name</p>
            <p className="mt-1 text-lg font-extrabold">{wallet.bankName}</p>
          </div>
        </div>
      </div>

      <LoadingButton isLoading={loading} onClick={createVirtualAccount} className="mt-4 w-full bg-amber text-slate-900">
        Create Virtual Account
      </LoadingButton>

      <div className="mt-5 rounded-[28px] bg-white p-5 shadow-xl shadow-slate-200/70">
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Withdrawal Workflow</p>
        <h3 className="mt-1 text-xl font-black text-slate-900">Quick Payout</h3>
        <div className="mt-4 space-y-3">
          <input className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" placeholder="Amount" value={withdrawForm.amount} onChange={(e) => setWithdrawForm((current) => ({ ...current, amount: e.target.value }))} />
          <select className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" value={withdrawForm.bankCode} onChange={(e) => setWithdrawForm((current) => ({ ...current, bankCode: e.target.value }))}>
            <option value="">Select Bank</option>
            {banks.map((b) => (
              <option key={b.code} value={b.code}>{b.name}</option>
            ))}
          </select>
          <input className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" placeholder="Account Number" value={withdrawForm.accountNumber} onChange={(e) => setWithdrawForm((current) => ({ ...current, accountNumber: e.target.value }))} />
          <LoadingButton isLoading={loading} onClick={withdraw} className="w-full bg-forest text-white">Withdraw Funds</LoadingButton>
        </div>
      </div>
    </div>
  );
}
