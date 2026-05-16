import React, { useRef, useState } from 'react';
import { Link2, Mic, ScanLine, ChevronRight, Sun, Moon } from 'lucide-react';
import { useApp } from '../context/AppContext';
import MicOverlay from '../components/MicOverlay';
import ReviewModal from '../components/ReviewModal';
import LoadingButton from '../components/LoadingButton';

export default function DashboardScreen() {
  const {
    profile,
    activities,
    loading,
    voiceOverlayOpen,
    setVoiceOverlayOpen,
    paymentModalOpen,
    setPaymentModalOpen,
    paymentForm,
    setPaymentForm,
    processVoice,
    processLedger,
    generatePaymentLink,
    createVirtualAccount,
    wallet,
    reviewState,
    setReviewState,
    confirmReview,
    theme,
    toggleTheme,
  } = useApp();

  const ledgerInputRef = useRef(null);
  const [micActive, setMicActive] = useState(false);

  const trustScore = profile?.trustScore ?? 43;
  const tierName = profile?.tierName ?? 'New';

  const [profilePanelOpen, setProfilePanelOpen] = React.useState(false);

  return (
    <div className="relative min-h-screen px-4 pb-6 pt-4">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.3em] text-forest">SmartSync Hub</p>
          <h2 className="text-2xl font-black text-slate-900">Hello, {profile?.name?.split(' ')?.[0] || 'Trader'}</h2>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={toggleTheme} title="Toggle theme" className="rounded-full bg-white p-2 shadow-md">
            {theme === 'dark' ? <Sun size={18} className="text-amber" /> : <Moon size={18} className="text-forest" />}
          </button>
          <button onClick={() => setProfilePanelOpen(true)} className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-slate-900 shadow-md">
            {profile?.name ? profile.name.charAt(0).toUpperCase() : 'U'}
          </button>
        </div>
      </div>

      <div className="rounded-[28px] bg-gradient-to-br from-forest to-[#0a3e44] p-5 text-white shadow-2xl shadow-forest/20">
        <p className="text-xs uppercase tracking-[0.3em] text-white/70">Credit Score</p>
        <div className="mt-2 flex items-end justify-between gap-4">
          <div>
            <h3 className="text-4xl font-black">{trustScore}/100</h3>
            <p className="mt-1 text-sm text-white/80">Current badge: {tierName}</p>
          </div>
          <div className="rounded-2xl bg-white/15 px-4 py-3 text-right backdrop-blur">
            <p className="text-xs uppercase tracking-[0.25em] text-white/60">Market Mode</p>
            <p className="mt-1 text-lg font-extrabold text-amber">Ready</p>
          </div>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-3 gap-3">
        <button
          onClick={() => {
            console.log('DEBUG: Speak Record tapped');
            setMicActive(true);
            setVoiceOverlayOpen(true);
          }}
          className="rounded-[24px] bg-white p-4 text-left shadow-lg shadow-slate-200/70"
        >
          <Mic className="text-forest" size={20} />
          <p className="mt-3 text-sm font-bold text-slate-900">🎤 Speak Record</p>
        </button>
        <button
          onClick={() => {
            console.log('DEBUG: Scan Ledger tapped');
            ledgerInputRef.current?.click();
          }}
          className="rounded-[24px] bg-white p-4 text-left shadow-lg shadow-slate-200/70"
        >
          <ScanLine className="text-forest" size={20} />
          <p className="mt-3 text-sm font-bold text-slate-900">📸 Scan Ledger</p>
        </button>
        <button
          onClick={() => {
            console.log('DEBUG: Payment Link tapped');
            setPaymentModalOpen(true);
          }}
          className="rounded-[24px] bg-white p-4 text-left shadow-lg shadow-slate-200/70"
        >
          <Link2 className="text-forest" size={20} />
          <p className="mt-3 text-sm font-bold text-slate-900">🔗 Payment Link</p>
        </button>
      </div>

      <input
        ref={ledgerInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) return;
          console.log('DEBUG: Ledger file selected', file.name);
          await processLedger(file);
          event.target.value = '';
        }}
      />

      <div className="mt-5 flex items-center justify-between">
        <h3 className="text-lg font-extrabold text-slate-900">Recent Transactions</h3>
        <button className="text-sm font-semibold text-forest">View all</button>
      </div>

      <div className="mt-3 max-h-[34vh] space-y-3 overflow-y-auto pb-2 scrollbar-hide">
        {activities.length === 0 ? (
          <div className="rounded-[22px] border-dashed border-2 border-slate-200 p-6 text-center">
            <p className="font-bold text-slate-800">No recent transactions logged yet.</p>
            <p className="mt-2 text-sm text-slate-500">Tap the mic or scan a ledger page to start!</p>
          </div>
        ) : (
          activities.map((item) => (
            <div key={item.id} className="rounded-[22px] bg-white p-4 shadow-md shadow-slate-200/70">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-bold text-slate-900">{item.item}</p>
                  <p className="mt-1 text-xs text-slate-500">{item.timestamp} • {item.verified ? 'Verified' : 'Pending'}</p>
                </div>
                <p className={`text-sm font-black ${item.type === 'SALE' || item.type === 'CREDIT' ? 'text-emerald-600' : 'text-rose-500'}`}>
                  {(item.type === 'SALE' || item.type === 'CREDIT' ? '+' : '-') + '₦' + Number(item.amount).toLocaleString()}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-5 rounded-[26px] bg-white p-4 shadow-xl shadow-slate-200/70">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.25em] text-slate-400">Wallet Quick Action</p>
            <h4 className="mt-1 text-lg font-black text-slate-900">Virtual Account</h4>
          </div>
          <ChevronRight className="text-slate-400" />
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-2xl bg-[#F8F9FA] p-3">
            <p className="text-xs text-slate-500">Account</p>
            <p className="mt-1 font-bold text-slate-900">{wallet.accountNumber || 'Not created yet'}</p>
          </div>
          <div className="rounded-2xl bg-[#F8F9FA] p-3">
            <p className="text-xs text-slate-500">Bank</p>
            <p className="mt-1 font-bold text-slate-900">{wallet.bankName}</p>
          </div>
        </div>
        <LoadingButton
          isLoading={loading}
          onClick={createVirtualAccount}
          className="mt-4 w-full bg-amber text-slate-900"
        >
          Create / Refresh Virtual Account
        </LoadingButton>
      </div>

      {voiceOverlayOpen && (
        <MicOverlay
          open={voiceOverlayOpen}
          onClose={() => {
            setVoiceOverlayOpen(false);
            setMicActive(false);
          }}
          onPickVoice={async (file) => {
            console.log('DEBUG: Mic overlay picked file', file.name);
            await processVoice(file);
            setVoiceOverlayOpen(false);
            setMicActive(false);
          }}
        />
      )}

      {paymentModalOpen && (
        <div className="absolute inset-0 z-40 flex items-end bg-slate-950/50 px-4 pb-4 backdrop-blur-sm">
          <div className="w-full rounded-[28px] bg-white p-5 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">Payment Link</h3>
              <button onClick={() => setPaymentModalOpen(false)} className="rounded-full bg-slate-100 px-3 py-2 text-sm font-bold text-slate-600">Close</button>
            </div>
            <div className="space-y-3">
              <input className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" placeholder="Amount" value={paymentForm.amount} onChange={(e) => setPaymentForm((current) => ({ ...current, amount: e.target.value }))} />
              <input className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" placeholder="Customer Email" value={paymentForm.email} onChange={(e) => setPaymentForm((current) => ({ ...current, email: e.target.value }))} />
              <input className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm" placeholder="Description" value={paymentForm.description} onChange={(e) => setPaymentForm((current) => ({ ...current, description: e.target.value }))} />
              <LoadingButton isLoading={loading} onClick={generatePaymentLink} className="w-full bg-forest text-white">Generate Link</LoadingButton>
            </div>
          </div>
        </div>
      )}

      {micActive && <div className="fixed bottom-5 right-5 z-30 rounded-full bg-amber px-3 py-2 text-xs font-bold text-slate-900 shadow-lg">Mic Active</div>}

      <ReviewModal
        open={reviewState.open}
        transaction={reviewState.transaction}
        loading={loading}
        onClose={() => setReviewState({ open: false, transaction: null, jobId: null })}
        onChange={(field, value) => {
          setReviewState((current) => ({
            ...current,
            transaction: {
              ...current.transaction,
              [field]: value,
            },
          }));
        }}
        onConfirm={async () => {
          if (!reviewState.transaction) return;
          await confirmReview({
            ...reviewState.transaction,
            amount: Number(reviewState.transaction.amount),
            quantity: Number(reviewState.transaction.quantity),
            unit: reviewState.transaction.unit || 'item',
            type: reviewState.transaction.type || 'SALE',
            notes: reviewState.transaction.notes || '',
          });
        }}
      />
    </div>
  );
}
