import React from 'react';
import { FileSpreadsheet, History, Settings, PlusCircle, LayoutDashboard } from 'lucide-react';

interface NavbarProps {
  currentTab: 'dashboard' | 'session' | 'history' | 'settings';
  setCurrentTab: (tab: 'dashboard' | 'session' | 'history' | 'settings') => void;
  resetSession: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab, resetSession }) => {
  return (
    <header className="bg-[#2d333b] border-b border-[#444c56] px-4 sm:px-6 py-3 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
        <div className="bg-[#24292e] p-2 rounded-lg text-white shadow-md">
          <FileSpreadsheet className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            Smart Document Converter
            <span className="text-xs font-semibold uppercase px-2 py-0.5 bg-[#539bf5]/15 text-[#539bf5] border border-[#539bf5]/30 rounded-full">
              v1.0.0
            </span>
          </h1>
          <p className="text-xs text-[#adbac7]">Dynamic Excel-to-Word Automated Engine</p>
        </div>
      </div>

      <nav className="flex items-center flex-wrap gap-1.5 sm:gap-2">
        <button
          onClick={() => setCurrentTab('dashboard')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
            currentTab === 'dashboard'
              ? 'bg-[#373e47] text-white shadow-sm'
              : 'text-[#cdd9e5] hover:text-white hover:bg-[#373e47]/60'
          }`}
        >
          <LayoutDashboard className="w-4 h-4" />
          <span>Dashboard</span>
        </button>

        <button
          onClick={() => {
            resetSession();
            setCurrentTab('session');
          }}
          className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-sm font-semibold transition shadow-sm ${
            currentTab === 'session'
              ? 'bg-[#347d39] text-white hover:bg-[#46954a]'
              : 'bg-[#2d333b] text-[#cdd9e5] hover:bg-[#347d39]'
          }`}
        >
          <PlusCircle className="w-4 h-4" />
          <span>New Conversion</span>
        </button>

        <button
          onClick={() => setCurrentTab('history')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
            currentTab === 'history'
              ? 'bg-[#373e47] text-white shadow-sm'
              : 'text-[#cdd9e5] hover:text-white hover:bg-[#373e47]/60'
          }`}
        >
          <History className="w-4 h-4" />
          <span>History</span>
        </button>

        <button
          onClick={() => setCurrentTab('settings')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition ${
            currentTab === 'settings'
              ? 'bg-[#373e47] text-white shadow-sm'
              : 'text-[#cdd9e5] hover:text-white hover:bg-[#373e47]/60'
          }`}
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
      </nav>
    </header>
  );
};
