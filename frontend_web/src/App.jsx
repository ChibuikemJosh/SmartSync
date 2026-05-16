import React from 'react';
import Frame from './components/Frame';
import Toast from './components/Toast';
import AuthScreen from './screens/AuthScreen';
import MobileShell from './components/MobileShell';
import { useApp } from './context/AppContext';

export default function App() {
  const { initialized, token, profile, toast } = useApp();

  return (
    <Frame>
      <Toast toast={toast} />
      {!initialized ? (
        <div className="flex min-h-screen items-center justify-center">
          <div className="flex flex-col items-center gap-3 text-slate-700">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-forest/30 border-t-forest" />
            <p className="text-sm font-semibold">Loading SmartSync...</p>
          </div>
        </div>
      ) : token && profile ? (
        <MobileShell />
      ) : (
        <AuthScreen />
      )}
    </Frame>
  );
}
