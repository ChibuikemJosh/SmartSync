import React, { useState } from 'react';
import { MessageSquareText, LayoutDashboard, Wallet } from 'lucide-react';
import DashboardScreen from '../screens/DashboardScreen';
import WalletScreen from '../screens/WalletScreen';
import ChatScreen from '../screens/ChatScreen';
import { useApp } from '../context/AppContext';

const tabs = [
  { id: 'dashboard', label: 'Home', icon: LayoutDashboard, element: <DashboardScreen /> },
  { id: 'wallet', label: 'Wallet', icon: Wallet, element: <WalletScreen /> },
  { id: 'chat', label: 'Chat', icon: MessageSquareText, element: <ChatScreen /> },
];

export default function MobileShell() {
  const { logout } = useApp();
  const [activeTab, setActiveTab] = useState('dashboard');

  const active = tabs.find((tab) => tab.id === activeTab) || tabs[0];

  return (
    <div className="relative min-h-screen pb-20">
      <div>{active.element}</div>

      <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 bg-white/95 px-3 py-3 backdrop-blur">
        <div className="grid grid-cols-4 gap-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const selected = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex flex-col items-center justify-center rounded-2xl py-3 text-xs font-bold ${selected ? 'bg-forest text-white' : 'text-slate-500'}`}
              >
                <Icon size={18} />
                <span className="mt-1">{tab.label}</span>
              </button>
            );
          })}
          <button
            onClick={logout}
            className="flex flex-col items-center justify-center rounded-2xl py-3 text-xs font-bold text-slate-500"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
