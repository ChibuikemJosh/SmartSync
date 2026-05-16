import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import LoadingButton from '../components/LoadingButton';
import { useApp } from '../context/AppContext';

export default function AuthScreen() {
  const { login, register, loading } = useApp();
  const [isLoginView, setIsLoginView] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    city: 'Lagos',
    state: 'Lagos',
  });
  const [selectedRole, setSelectedRole] = useState('Trader');

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const handleAuth = async () => {
    if (isLoginView) {
      await login(form.email, form.password);
      return;
    }

    const userData = {
      id: `user_${Date.now()}`,
      name: form.name.trim(),
      email: form.email.trim(),
      password: form.password,
      role: selectedRole,
      location: {
        city: form.city.trim(),
        state: form.state.trim(),
        country: 'Nigeria',
      },
    };

    await register(userData);
  };

  return (
    <div className="flex min-h-screen flex-col justify-center px-5 py-10">
      <div className="mb-8 text-center">
        <p className="text-xs font-bold uppercase tracking-[0.3em] text-forest">SmartSync</p>
        <h1 className="mt-2 text-3xl font-black text-slate-900">Market Intelligence</h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">Mobile-first web app for traders and gig workers.</p>
      </div>

      <div className="rounded-[28px] bg-white p-5 shadow-2xl shadow-slate-200/80">
        <div className="grid grid-cols-2 gap-3 rounded-2xl bg-slate-100 p-1">
          <button
            onClick={() => setIsLoginView(true)}
            className={`rounded-2xl py-3 text-sm font-bold transition ${isLoginView ? 'bg-forest text-white' : 'text-slate-600'}`}
          >
            Sign In
          </button>
          <button
            onClick={() => setIsLoginView(false)}
            className={`rounded-2xl py-3 text-sm font-bold transition ${!isLoginView ? 'bg-forest text-white' : 'text-slate-600'}`}
          >
            Create Account
          </button>
        </div>

        <div className="mt-5 space-y-4">
          {!isLoginView && (
            <>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm"
                placeholder="Full Name"
                value={form.name}
                onChange={(e) => update('name', e.target.value)}
              />
              <div className="grid grid-cols-2 gap-3">
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm"
                  placeholder="City"
                  value={form.city}
                  onChange={(e) => update('city', e.target.value)}
                />
                <input
                  className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm"
                  placeholder="State"
                  value={form.state}
                  onChange={(e) => update('state', e.target.value)}
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                {['Trader', 'Worker', 'Both'].map((role) => (
                  <button
                    key={role}
                    onClick={() => setSelectedRole(role)}
                    className={`rounded-2xl px-3 py-2 text-xs font-bold ${selectedRole === role ? 'bg-amber text-slate-900' : 'bg-slate-100 text-slate-600'}`}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </>
          )}

          <input
            className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 text-sm"
            placeholder="Email"
            value={form.email}
            onChange={(e) => update('email', e.target.value)}
          />

          <div className="relative">
            <input
              className="w-full rounded-2xl border border-slate-200 bg-[#F8F9FA] px-4 py-3 pr-12 text-sm"
              placeholder="Password"
              type={showPassword ? 'text' : 'password'}
              value={form.password}
              onChange={(e) => update('password', e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-slate-500"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <LoadingButton
            isLoading={loading}
            onClick={handleAuth}
            className="w-full bg-forest text-white shadow-lg shadow-forest/20"
          >
            {isLoginView ? 'Login' : 'Create Account'}
          </LoadingButton>
        </div>
      </div>
    </div>
  );
}
