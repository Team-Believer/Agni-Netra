'use client';

import React from 'react';
import { Flame, Search, LogOut } from 'lucide-react';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchQuery, onSearchChange }) => {
  const username = 'Analyst';
  const initial = username.charAt(0).toUpperCase();

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-2.5 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      {/* Brand & Tagline */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-600">
          <Flame className="w-5 h-5 fill-orange-500 text-orange-600" />
        </div>
        <div>
          <div className="flex items-baseline gap-2">
            <h1 className="text-lg font-bold tracking-tight text-slate-900 leading-tight">Agni-Netra</h1>
          </div>
          <p className="text-[11px] text-slate-500 font-medium leading-none">
            Turning Thermal Data into Safer Tomorrows
          </p>
        </div>
      </div>

      {/* Global Search Bar */}
      <div className="flex-1 max-w-lg mx-8">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search location, facility, event ID..."
            className="w-full bg-slate-50 border border-slate-200 rounded-full pl-9 pr-4 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:bg-white transition-colors"
          />
        </div>
      </div>

      {/* Right User & Actions */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2.5 cursor-pointer hover:opacity-90 transition-opacity">
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-semibold">
            {initial}
          </div>
          <div className="text-left">
            <div className="text-xs font-semibold text-slate-900 leading-tight">{username}</div>
            <div className="text-[10px] text-slate-500 leading-none">Team Member</div>
          </div>
          <button 
            className="ml-2 p-1.5 rounded-full hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
