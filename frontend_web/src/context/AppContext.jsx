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

const initialActivities = [];

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
  const [paymentForm, setPaymentForm] = useState({ amount: '', email: '', description: '' });
  const [withdrawForm, setWithdrawForm] = useState({ amount: '', bankCode: '', accountNumber: '' });
  const [loadingIndicator, setLoadingIndicator] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

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

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

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
        // background create VA if missing
        setTimeout(() => {
          if (me && (!wallet.accountNumber || wallet.accountNumber === '')) {
            createVirtualAccount().catch((e) => console.log('VA auto-create error', e));
          }
        }, 1000);
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
      if (success) {
        setTimeout(() => {
          createVirtualAccount().catch((e) => console.log('VA auto-create error', e));
        }, 1200);
      }
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
      const body = {
        item: String(payload.item || ''),
        amount: Number(payload.amount || 0),
        quantity: parseInt(payload.quantity || 1, 10),
        unit: String(payload.unit || 'item'),
        type: String(payload.type || 'SALE'),
        notes: String(payload.notes || ''),
      };

      const response = await confirmTransactionRequest(body);
      setActivities((current) => [
        {
          id: `${Date.now()}`,
          item: body.item,
          amount: body.amount,
          type: body.type,
          verified: response.verified,
          timestamp: 'Now',
        },
        ...current,
      ]);
      setReviewState({ open: false, transaction: null, jobId: null });
      showToast(`Credit score updated to ${response.new_score}`, 'amber');
      return response;
    } catch (error) {
      console.log('DEBUG: confirm transaction error', error);
      window.alert('Could not log transaction. ' + (error?.message || ''));
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
    if (!profile) return null;
    setLoading(true);
    try {
      const response = await createVirtualAccountRequest({
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
      window.alert('Could not create virtual account. ' + (error?.message || ''));
      return null;
    } finally {
      setLoading(false);
    }
  };

  const generatePaymentLink = async () => {
    if (!profile) return null;
    setLoading(true);
    try {
      const response = await generatePaymentLinkRequest({
        amount: Number(paymentForm.amount || 0),
        email: paymentForm.email || profile.email,
        description: paymentForm.description || '',
      });
      setPaymentModalOpen(false);
      showToast('Payment link generated', 'forest');
      return response;
    } catch (error) {
      console.log('DEBUG: generate payment link error', error);
      window.alert('Could not generate payment link. ' + (error?.message || ''));
      return null;
    } finally {
      setLoading(false);
    }
  };

  const withdraw = async () => {
    setLoading(true);
    try {
      const response = await withdrawRequest({
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

  const value = useMemo(
    () => ({
      initialized,
      loading,
      token,
      profile,
      toast,
      theme,
      toggleTheme,
      reviewState,
      wallet,
      chatMessages,
      activities,
      voiceOverlayOpen,
      paymentModalOpen,
      paymentForm,
      withdrawForm,
      setPaymentForm,
      setWithdrawForm,
      setVoiceOverlayOpen,
      setPaymentModalOpen,
      setActivities,
      setProfile,
      setToast,
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
      loadingIndicator,
      setLoadingIndicator,
      updateProfile: (updates) => {
        setProfile((cur) => normalizeProfile({ ...cur, ...updates }));
        showToast('Profile updated', 'forest');
      },
    }),
    [
      initialized,
      loading,
      token,
      profile,
      toast,
      theme,
      reviewState,
      wallet,
      chatMessages,
      activities,
      voiceOverlayOpen,
      paymentModalOpen,
      paymentForm,
      withdrawForm,
      loadingIndicator,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used inside AppProvider');
  return context;
}
