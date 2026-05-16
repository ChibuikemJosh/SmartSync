import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import {
  chatRequest,
  confirmTransactionRequest,
  createVirtualAccountRequest,
  fetchAiStatusRequest,
  fetchMeRequest,
  generatePaymentLinkRequest,
  loginRequest,
  processLedgerRequest,
  processVoiceRequest,
  registerRequest,
  withdrawRequest,
} from '../services/api';

const AppContext = createContext(null);

const initialMessages = [
  {
    id: 'welcome',
    sender: 'bot',
    text: 'Oya welcome. I fit help you track sales, expenses and balances with market-style clarity.',
    time: 'Now',
  },
];

const initialActivities = [
  { id: '1', item: 'Tomatoes', amount: 12500, type: 'SALE', verified: true, timestamp: 'Today' },
  { id: '2', item: 'Transport', amount: 3000, type: 'EXPENSE', verified: true, timestamp: 'Today' },
];

function normalizeProfile(profile) {
  const tierName = profile?.tier?.name || profile?.tierName || 'New';
  const trustScore = profile?.trust_score ?? profile?.trustScore ?? 43;
  return {
    ...profile,
    trustScore,
    tierName,
  };
}

export function AppProvider({ children }) {
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [profile, setProfile] = useState(null);
  const [toast, setToast] = useState(null);
  const [reviewState, setReviewState] = useState({ open: false, transaction: null, jobId: null });
  const [wallet, setWallet] = useState({ accountNumber: '', bankName: 'GTBank / Squad', merchantTitle: '' });
  const [chatMessages, setChatMessages] = useState(initialMessages);
  const [activities, setActivities] = useState(initialActivities);
  const [voiceOverlayOpen, setVoiceOverlayOpen] = useState(false);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [paymentForm, setPaymentForm] = useState({ amount: '', transactionId: '', description: '' });
  const [withdrawForm, setWithdrawForm] = useState({ amount: '', bankCode: '', accountNumber: '' });

  useEffect(() => {
    let active = true;

    async function boot() {
      const storedToken = localStorage.getItem('token');
      if (!storedToken) {
        setInitialized(true);
        return;
      }

      try {
        const me = await fetchMeRequest();
        if (!active) return;
        setProfile(normalizeProfile(me));
        setToken(storedToken);
      } catch (error) {
        console.log('DEBUG: bootstrap token invalid', error);
        if (!active) return;
        if (localStorage.getItem('token') === storedToken) {
          localStorage.removeItem('token');
          setToken(null);
          setProfile(null);
        }
      } finally {
        if (active) setInitialized(true);
      }
    }

    boot();

    return () => {
      active = false;
    };
  }, []);

  const showToast = (message, tone = 'forest') => {
    setToast({ id: Date.now(), message, tone });
    window.clearTimeout(window.__smartsyncToastTimer);
    window.__smartsyncToastTimer = window.setTimeout(() => setToast(null), 2600);
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const trimmedEmail = email.trim();
      const trimmedPassword = password.trim();
      const data = await loginRequest(trimmedEmail, trimmedPassword);
      const accessToken = data.access_token;
      if (!accessToken) throw new Error('Missing access token');
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
      try {
        const me = await fetchMeRequest();
        setProfile(normalizeProfile(me));
      } catch (profileError) {
        console.log('DEBUG: profile hydration skipped after login', profileError);
        setProfile((current) => current || { id: '', name: trimmedEmail, email: trimmedEmail, trustScore: 43, tierName: 'New' });
      }
      showToast('Login passed! Welcome back.', 'forest');
      return true;
    } catch (error) {
      console.log('DEBUG: login error', error);
      window.alert(`Couldn't login. ${error?.message || 'Check details.'}`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const payload = {
        ...userData,
        name: userData.name.trim(),
        email: userData.email.trim(),
        password: userData.password.trim(),
        location: {
          ...userData.location,
          city: userData.location.city.trim(),
          state: userData.location.state.trim(),
        },
      };

      await registerRequest(payload);
      showToast('Created account successfully!', 'amber');
      const success = await login(payload.email, payload.password);
      return success;
    } catch (error) {
      console.log('DEBUG: register error', error);
      window.alert(`Couldn't create account. ${error?.message || 'Please try again.'}`);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setProfile(null);
    setReviewState({ open: false, transaction: null, jobId: null });
    showToast('Logged out', 'forest');
  };

  const openReviewForJob = async (jobId) => {
    setLoading(true);
    try {
      let status = await fetchAiStatusRequest(jobId);
      while ((status.status || '').toLowerCase() === 'processing') {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        status = await fetchAiStatusRequest(jobId);
      }

      const payload = status.result || status.transaction || status.extracted_data || status.data || status;
      setReviewState({
        open: true,
        transaction: {
          item: payload.item || '',
          amount: payload.amount || 0,
          quantity: payload.quantity || 1,
          unit: payload.unit || 'item',
          type: payload.type || 'SALE',
          notes: payload.notes || '',
        },
        jobId,
      });
    } catch (error) {
      console.log('DEBUG: ai status error', error);
      window.alert('AI record no finish properly. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const confirmReview = async (payload) => {
    setLoading(true);
    try {
      const response = await confirmTransactionRequest(payload);
      setActivities((current) => [
        {
          id: `${Date.now()}`,
          item: payload.item,
          amount: payload.amount,
          type: payload.type,
          verified: response.verified,
          timestamp: 'Now',
        },
        ...current,
      ]);
      setReviewState({ open: false, transaction: null, jobId: null });
      showToast(`Trust score updated to ${response.new_score}`, 'amber');
      return response;
    } catch (error) {
      console.log('DEBUG: confirm transaction error', error);
      window.alert('Could not log transaction.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const processVoice = async (file) => {
    setLoading(true);
    try {
      const response = await processVoiceRequest(file);
      await openReviewForJob(response.job_id);
    } catch (error) {
      console.log('DEBUG: process voice error', error);
      window.alert('Voice file upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const processLedger = async (file) => {
    setLoading(true);
    try {
      const response = await processLedgerRequest(file);
      await openReviewForJob(response.job_id);
    } catch (error) {
      console.log('DEBUG: process ledger error', error);
      window.alert('Ledger scan failed.');
    } finally {
      setLoading(false);
    }
  };

  const createVirtualAccount = async () => {
    if (!profile) return;
    setLoading(true);
    try {
      const response = await createVirtualAccountRequest({
        merchant_id: profile.id,
        business_name: profile.name || 'SmartSync Merchant',
        email: profile.email,
        phone: '08000000000',
      });
      setWallet({
        accountNumber: response.account_number || '',
        bankName: response.bank_name || 'GTBank / Squad',
        merchantTitle: profile.name || 'Merchant',
      });
      showToast('Virtual account created', 'forest');
      return response;
    } catch (error) {
      console.log('DEBUG: create virtual account error', error);
      window.alert('Could not create virtual account.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const generatePaymentLink = async () => {
    if (!profile) return;
    setLoading(true);
    try {
      const response = await generatePaymentLinkRequest({
        user_id: profile.id,
        merchant_id: profile.id,
        amount: Number(paymentForm.amount || 0),
        transaction_id: paymentForm.transactionId || `${Date.now()}`,
        description: paymentForm.description || 'Payment for goods/services',
        email: profile.email,
      });
      window.open(response.checkout_url, '_blank', 'noopener,noreferrer');
      showToast('Payment link opened', 'amber');
      setPaymentModalOpen(false);
      return response;
    } catch (error) {
      console.log('DEBUG: payment link error', error);
      window.alert('Could not create payment link.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const withdraw = async () => {
    if (!profile) return;
    setLoading(true);
    try {
      const response = await withdrawRequest({
        user_id: profile.id,
        amount: Number(withdrawForm.amount || 0),
        bank_code: withdrawForm.bankCode,
        account_number: withdrawForm.accountNumber,
      });
      showToast(`Withdrawal sent: ${response.reference}`, 'forest');
      return response;
    } catch (error) {
      console.log('DEBUG: withdraw error', error);
      window.alert('Withdrawal failed.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const sendChat = async (message, voicePath = null) => {
    const safeMessage = message.trim();
    if (!safeMessage && !voicePath) return;

    const userBubble = {
      id: `${Date.now()}-user`,
      sender: 'user',
      text: safeMessage || 'Voice note sent',
      time: 'Now',
    };
    setChatMessages((current) => [...current, userBubble]);

    try {
      const response = await chatRequest({ message: safeMessage, voice_path: voicePath });
      const botBubble = {
        id: `${Date.now()}-bot`,
        sender: 'bot',
        text: response.answer || 'No worry, I no see result yet.',
        time: 'Now',
      };
      setChatMessages((current) => [...current, botBubble]);
      return response;
    } catch (error) {
      console.log('DEBUG: chat error', error);
      const botBubble = {
        id: `${Date.now()}-bot`,
        sender: 'bot',
        text: 'E get error for backend, but I still dey with you.',
        time: 'Now',
      };
      setChatMessages((current) => [...current, botBubble]);
      return null;
    }
  };

  const value = useMemo(
    () => ({
      initialized,
      loading,
      token,
      profile,
      toast,
      reviewState,
      wallet,
      chatMessages,
      activities,
      voiceOverlayOpen,
      setVoiceOverlayOpen,
      paymentModalOpen,
      setPaymentModalOpen,
      paymentForm,
      setPaymentForm,
      withdrawForm,
      setWithdrawForm,
      login,
      register,
      logout,
      openReviewForJob,
      confirmReview,
      processVoice,
      processLedger,
      createVirtualAccount,
      generatePaymentLink,
      withdraw,
      sendChat,
      setReviewState,
    }),
    [
      activities,
      chatMessages,
      confirmReview,
      createVirtualAccount,
      generatePaymentLink,
      initialized,
      loading,
      login,
      logout,
      paymentForm,
      paymentModalOpen,
      profile,
      register,
      reviewState,
      sendChat,
      setVoiceOverlayOpen,
      toast,
      token,
      voiceOverlayOpen,
      wallet,
      withdraw,
      withdrawForm,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used inside AppProvider');
  return context;
}
